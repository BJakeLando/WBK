/* Website assistant chat widget — Watercolors By Karla
   Plain JavaScript, no dependencies. Message text is always rendered with
   textContent / createElement (never innerHTML), so replies can't inject HTML. */
(function () {
  'use strict';

  var root = document.getElementById('wbk-chat');
  var configEl = document.getElementById('wbk-chat-config');
  if (!root || !configEl || !window.fetch) return;

  var config;
  try {
    config = JSON.parse(configEl.textContent);
  } catch (e) {
    return;
  }

  var launcher = root.querySelector('.wbk-chat__launcher');
  var panel = root.querySelector('.wbk-chat__panel');
  var log = root.querySelector('.wbk-chat__log');
  var form = root.querySelector('.wbk-chat__form');
  var input = root.querySelector('.wbk-chat__input');
  var sendButton = root.querySelector('.wbk-chat__send');
  var csrfToken = root.getAttribute('data-csrf') || '';

  var OPEN_KEY = 'wbkChatOpen';
  var TEASER_KEY = 'wbkChatTeaserSeen';
  var SOCIAL_HOSTS = ['instagram.com', 'tiktok.com', 'etsy.com', 'facebook.com'];
  var isPhone = window.matchMedia('(max-width: 575.98px)');
  var finePointer = window.matchMedia('(pointer: fine)');

  var historyLoaded = false;
  var sending = false;

  // sessionStorage can be unavailable (private mode, blocked cookies): never let that break the chat.
  function remember(key, value) {
    try {
      if (value === null) window.sessionStorage.removeItem(key);
      else window.sessionStorage.setItem(key, value);
    } catch (e) { /* ignore */ }
  }

  function recall(key) {
    try {
      return window.sessionStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }

  // ── Safe, minimal markdown: **bold**, *italic*, [links](/path/), lists ─────

  var INLINE = /\*\*([^*\n]+)\*\*|\[([^\]\n]+)\]\(([^)\s]+)\)|(https?:\/\/[^\s<>()]+[^\s<>().,!?;:'"])|([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})|\*([^*\n]+)\*/g;

  function classifyHref(raw) {
    var href = String(raw || '').trim();
    if (/^mailto:[^\s@]+@[^\s@]+\.[^\s@]+$/i.test(href)) return { href: href };
    var url;
    try {
      url = new URL(href, window.location.href);
    } catch (e) {
      return null;
    }
    if (url.protocol !== 'https:' && url.protocol !== 'http:') return null;
    var host = url.hostname.toLowerCase().replace(/^www\./, '');
    if (url.origin === window.location.origin || host === 'paintedbykarla.com') {
      return {
        href: url.pathname + url.search + url.hash,
        internal: true,
        booking: url.pathname.indexOf(config.bookUrl) === 0
      };
    }
    for (var i = 0; i < SOCIAL_HOSTS.length; i++) {
      var allowed = SOCIAL_HOSTS[i];
      if (host === allowed || host.slice(-(allowed.length + 1)) === '.' + allowed) {
        return { href: url.href, external: true };
      }
    }
    return null; // unknown site: show the text, but don't link it
  }

  function makeLink(label, href) {
    var target = classifyHref(href);
    if (!target) return document.createTextNode(label);
    var link = document.createElement('a');
    link.textContent = label;
    link.href = target.href;
    if (target.external) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    }
    if (target.internal) link.setAttribute('data-internal', '');
    if (target.booking) link.setAttribute('data-booking', '');
    return link;
  }

  function appendInline(parent, text) {
    var pattern = new RegExp(INLINE.source, 'g');
    var last = 0;
    var match;
    while ((match = pattern.exec(text)) !== null) {
      if (match.index > last) parent.appendChild(document.createTextNode(text.slice(last, match.index)));
      if (match[1]) {
        var strong = document.createElement('strong');
        strong.textContent = match[1];
        parent.appendChild(strong);
      } else if (match[2]) {
        parent.appendChild(makeLink(match[2], match[3]));
      } else if (match[4]) {
        parent.appendChild(makeLink(match[4], match[4]));
      } else if (match[5]) {
        parent.appendChild(makeLink(match[5], 'mailto:' + match[5]));
      } else if (match[6]) {
        var em = document.createElement('em');
        em.textContent = match[6];
        parent.appendChild(em);
      }
      last = pattern.lastIndex;
    }
    if (last < text.length) parent.appendChild(document.createTextNode(text.slice(last)));
  }

  function renderRich(container, text) {
    var list = null;
    var listType = '';
    var paragraph = null;

    String(text).replace(/\r\n?/g, '\n').split('\n').forEach(function (raw) {
      var line = raw.replace(/\s+$/, '');
      var bullet = /^\s*[-*•]\s+(.*)$/.exec(line);
      var numbered = bullet ? null : /^\s*(\d+)[.)]\s+(.*)$/.exec(line);

      if (bullet || numbered) {
        var type = bullet ? 'ul' : 'ol';
        if (!list || listType !== type) {
          list = document.createElement(type);
          if (numbered && numbered[1] !== '1') list.start = parseInt(numbered[1], 10);
          container.appendChild(list);
          listType = type;
        }
        var item = document.createElement('li');
        appendInline(item, bullet ? bullet[1] : numbered[2]);
        list.appendChild(item);
        paragraph = null;
        return;
      }
      if (!line.trim()) {
        paragraph = null;
        return;
      }
      list = null;
      var heading = /^#{1,6}\s+(.*)$/.exec(line);
      if (heading) {
        var headingPara = document.createElement('p');
        var headingText = document.createElement('strong');
        headingText.textContent = heading[1];
        headingPara.appendChild(headingText);
        container.appendChild(headingPara);
        paragraph = null;
        return;
      }
      if (!paragraph) {
        paragraph = document.createElement('p');
        container.appendChild(paragraph);
      } else {
        paragraph.appendChild(document.createElement('br'));
      }
      appendInline(paragraph, line);
    });

    // Any mention of the booking form gets a proper "Book Your Date" button.
    if (container.querySelector('a[data-booking]')) {
      var ctaWrap = document.createElement('p');
      var cta = document.createElement('a');
      cta.className = 'wbk-chat__cta';
      cta.href = config.bookUrl;
      cta.textContent = 'Book Your Date';
      cta.setAttribute('data-internal', '');
      ctaWrap.appendChild(cta);
      container.appendChild(ctaWrap);
    }
  }

  // ── Conversation UI ───────────────────────────────────────────────────

  function scrollToBottom() {
    log.scrollTop = log.scrollHeight;
  }

  // Long replies: show the start of the reply rather than its last line.
  function scrollToMessage(bubble) {
    if (bubble.offsetHeight > log.clientHeight - 24) {
      log.scrollTop = Math.max(bubble.offsetTop - 12, 0);
    } else {
      scrollToBottom();
    }
  }

  function addMessage(role, text) {
    var bubble = document.createElement('div');
    var isUser = role === 'user';
    bubble.className = 'wbk-chat__msg wbk-chat__msg--' + (isUser ? 'user' : 'bot');
    var speaker = document.createElement('span');
    speaker.className = 'wbk-chat__sr';
    speaker.textContent = isUser ? 'You said: ' : 'Assistant: ';
    if (isUser) {
      bubble.appendChild(speaker);
      bubble.appendChild(document.createTextNode(text));
    } else {
      renderRich(bubble, text);
      bubble.insertBefore(speaker, bubble.firstChild);
    }
    log.appendChild(bubble);
    // Only the newest "Book Your Date" button stays, so it doesn't repeat down the chat.
    if (bubble.querySelector('.wbk-chat__cta')) {
      Array.prototype.forEach.call(log.querySelectorAll('.wbk-chat__cta'), function (cta) {
        if (!bubble.contains(cta) && cta.parentNode) cta.parentNode.parentNode.removeChild(cta.parentNode);
      });
    }
    scrollToMessage(bubble);
    return bubble;
  }

  function showGreeting(withSuggestions) {
    var ornament = document.createElement('div');
    ornament.className = 'wbk-chat__ornament';
    ornament.setAttribute('aria-hidden', 'true');
    ornament.appendChild(document.createElement('span'));
    ornament.appendChild(document.createElement('i'));
    ornament.appendChild(document.createElement('span'));
    log.appendChild(ornament);
    addMessage('assistant', config.greeting);
    if (!withSuggestions) return;

    var chips = document.createElement('div');
    chips.className = 'wbk-chat__chips';
    chips.setAttribute('role', 'group');
    chips.setAttribute('aria-label', 'Suggested questions');
    (config.suggestions || []).forEach(function (label) {
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'wbk-chat__chip';
      chip.textContent = label;
      chip.addEventListener('click', function () {
        send(label);
      });
      chips.appendChild(chip);
    });
    log.appendChild(chips);
  }

  function removeNodes(selector) {
    Array.prototype.forEach.call(log.querySelectorAll(selector), function (node) {
      node.parentNode.removeChild(node);
    });
  }

  function showTyping() {
    var typing = document.createElement('div');
    typing.className = 'wbk-chat__typing';
    typing.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 3; i++) typing.appendChild(document.createElement('span'));
    log.appendChild(typing);
    scrollToBottom();
    return typing;
  }

  function showError(failedText, message) {
    var bubble = addMessage(
      'assistant',
      message || "Sorry, I couldn't connect just now. Please check your connection and try again."
    );
    bubble.classList.add('wbk-chat__msg--error');
    var retry = document.createElement('button');
    retry.type = 'button';
    retry.className = 'wbk-chat__retry';
    retry.textContent = 'Try again';
    retry.addEventListener('click', function () {
      bubble.parentNode.removeChild(bubble);
      post(failedText);
    });
    bubble.appendChild(retry);
    scrollToBottom();
  }

  function autosize() {
    input.style.height = '';
    if (!input.value) return; // back to the one-line height from the stylesheet
    input.style.height = Math.min(input.scrollHeight + 2, 120) + 'px';
  }

  // ── Talking to the server ─────────────────────────────────────────────

  function request(url, options) {
    var controller = window.AbortController ? new AbortController() : null;
    var timer = controller ? window.setTimeout(function () { controller.abort(); }, 60000) : null;
    options = options || {};
    options.credentials = 'same-origin';
    options.headers = Object.assign({ 'X-Requested-With': 'XMLHttpRequest' }, options.headers || {});
    if (controller) options.signal = controller.signal;

    function done() {
      if (timer) window.clearTimeout(timer);
    }

    return fetch(url, options).then(
      function (response) {
        done();
        return response.json().then(
          function (data) { return { ok: response.ok, status: response.status, data: data }; },
          function () { return { ok: response.ok, status: response.status, data: null }; }
        );
      },
      function (error) {
        done();
        throw error;
      }
    );
  }

  function post(text) {
    sending = true;
    sendButton.disabled = true;
    log.setAttribute('aria-busy', 'true');
    var typing = showTyping();

    function finish() {
      if (typing.parentNode) typing.parentNode.removeChild(typing);
      sending = false;
      sendButton.disabled = false;
      log.removeAttribute('aria-busy');
      if (finePointer.matches) input.focus();
    }

    request(config.messageUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ message: text, page: window.location.pathname })
    }).then(
      function (result) {
        finish();
        if (result.data && result.data.reply) {
          addMessage('assistant', result.data.reply);
        } else if (result.status === 403) {
          showError(text, 'This page has been open a while. Please refresh the page and ask again.');
        } else {
          showError(text, result.data && result.data.error);
        }
      },
      function () {
        finish();
        showError(text);
      }
    );
  }

  function send(rawText) {
    var text = String(rawText || '').trim();
    if (!text || sending) return;
    removeNodes('.wbk-chat__chips');
    removeNodes('.wbk-chat__msg--error');
    addMessage('user', text);
    input.value = '';
    autosize();
    post(text);
  }

  function loadHistory() {
    if (historyLoaded) return Promise.resolve();
    historyLoaded = true;
    return request(config.historyUrl, { method: 'GET' }).then(
      function (result) {
        var messages = (result.data && result.data.messages) || [];
        log.textContent = '';
        showGreeting(messages.length === 0);
        messages.forEach(function (message) {
          addMessage(message.role, message.content);
        });
      },
      function () {
        log.textContent = '';
        showGreeting(true);
      }
    );
  }

  // ── Open / close ──────────────────────────────────────────────────────

  function openChat(restoring) {
    root.classList.add('is-open');
    root.classList.remove('is-teasing');
    panel.hidden = false;
    launcher.setAttribute('aria-expanded', 'true');
    remember(OPEN_KEY, '1');
    remember(TEASER_KEY, '1');
    if (isPhone.matches) document.documentElement.classList.add('wbk-chat-lock');
    loadHistory().then(function () {
      scrollToBottom();
      if (!restoring && finePointer.matches) input.focus();
    });
  }

  function closeChat() {
    root.classList.remove('is-open');
    panel.hidden = true;
    launcher.setAttribute('aria-expanded', 'false');
    remember(OPEN_KEY, null);
    document.documentElement.classList.remove('wbk-chat-lock');
    launcher.focus();
  }

  launcher.addEventListener('click', function () {
    openChat(false);
  });

  root.querySelector('[data-chat-action="close"]').addEventListener('click', closeChat);

  root.querySelector('[data-chat-action="restart"]').addEventListener('click', function () {
    if (sending) return;
    request(config.resetUrl, { method: 'POST', headers: { 'X-CSRFToken': csrfToken } })
      .catch(function () { /* start fresh on screen regardless */ })
      .then(function () {
        log.textContent = '';
        historyLoaded = true;
        showGreeting(true);
        if (finePointer.matches) input.focus();
      });
  });

  // Escape closes the chat when focus is in it (or nowhere in particular, e.g.
  // right after it reopened on a new page). Other widgets keep their own Escape.
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape' || !root.classList.contains('is-open')) return;
    var active = document.activeElement;
    if (panel.contains(active) || !active || active === document.body) {
      event.preventDefault();
      closeChat();
    }
  });

  // On phones the chat covers the whole screen, so don't reopen it over the
  // page a visitor just tapped through to.
  panel.addEventListener('click', function (event) {
    var link = event.target.closest ? event.target.closest('a[data-internal], .wbk-chat__fineprint a') : null;
    if (link && isPhone.matches) remember(OPEN_KEY, null);
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    send(input.value);
  });

  input.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      send(input.value);
    }
  });

  input.addEventListener('input', autosize);

  // Keep the conversation open while a visitor browses (desktop only).
  if (recall(OPEN_KEY) === '1' && !isPhone.matches) {
    openChat(true);
  } else if (!recall(TEASER_KEY) && !isPhone.matches) {
    window.setTimeout(function () {
      if (root.classList.contains('is-open')) return;
      root.classList.add('is-teasing');
      remember(TEASER_KEY, '1');
      window.setTimeout(function () { root.classList.remove('is-teasing'); }, 8000);
    }, 4000);
  }
})();
