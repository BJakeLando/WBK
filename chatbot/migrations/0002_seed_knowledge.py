"""Starter knowledge for the website assistant.

Facts come from the live site (pricing sheet, How It Works, FAQ image, welcome
signs, homepage) plus the deposit terms Brandon confirmed on Sept 22, 2026.
Karla can edit all of this in the admin afterwards; this only runs once.
"""
import re

from django.db import migrations

FAQS = [
    (
        10,
        "What does Watercolors By Karla offer?",
        "Karla Lubbert is a professional watercolor artist. She offers:\n"
        "- Live wedding and event portraits: she paints your guests (and the newlyweds) live at your event.\n"
        "- Welcome signs that double as a guestbook.\n"
        "- In-studio commissions: custom watercolor portraits painted from your photos.\n"
        "- Pet portraits.\n"
        "Prints of her work are available upon request.",
    ),
    (
        20,
        "What is live painting?",
        "A wonderfully immersive art experience: Karla paints by hand at your event, creating "
        "watercolor portraits of your guests. It's entertainment plus unique keepsakes. Guests are "
        "welcome to watch and interact, which is why she usually starts at cocktail hour, when "
        "everyone is on site.",
    ),
    (
        30,
        "What are the live painting packages and prices?",
        "Live Guest Portrait packages:\n"
        "- Peonies Package, $1,300: 3 hours of on-site painting, starting at cocktail hour through "
        "the reception. Up to 50 guests (25 couples). Additional portraits completed in studio if "
        "needed, $20 each. Portraits are mailed as thank-you keepsakes.\n"
        "- Gold Package, $1,800: 4 hours of live painting starting at cocktail hour. Includes a "
        "complimentary 8x10\" portrait of the newlyweds. Up to 65 guests (33 couples). Additional "
        "portraits completed in studio if needed, $20 each. Portraits are mailed as thank-you "
        "keepsakes after the wedding.\n"
        "- Premium Package, $2,500: 5 hours of live painting, starting before the ceremony through "
        "the reception. Includes the newlyweds' 8x10\" portrait painted live. Up to 90 guests (45 "
        "couples). Leftover portraits are completed in studio, $10 each. Also includes a fun extra "
        "interaction canvas that guests can paint on, for even more memories.\n"
        "These prices apply to events in the Arizona White Mountains. Travel fees apply to all "
        "other locations.",
    ),
    (
        40,
        "Do you travel? Do prices change outside the White Mountains?",
        "Yes, Karla travels for events. She's based in the White Mountains of Arizona and has "
        "painted weddings in Colorado, Utah, Wyoming and New Zealand. The package prices only "
        "apply to the Arizona White Mountains; travel fees apply to all other locations, so Karla "
        "prepares a custom quote. Share your venue and date in the booking form to get one. "
        "Out-of-state event pricing is non-negotiable due to high travel expenses.",
    ),
    (
        50,
        "How does live painting work for guests?",
        "1. Guests pose for a quick photo. Karla just needs to see their outfits; faces are not "
        "detailed.\n"
        "2. Karla paints while they go enjoy the party.\n"
        "3. The first dozen portraits are finished at the event, and the rest are mailed to the "
        "couple to send as post-wedding thank-you cards.",
    ),
    (
        60,
        "How long does each portrait take?",
        "About 7 to 9 minutes for a half-body portrait with eyes only, and about 10 minutes for a "
        "full-body portrait with faces (not counting time spent chatting with guests). The bigger "
        "newlyweds' portrait is finished within 3 hours on the same day, and it's framed.",
    ),
    (
        70,
        "What does Karla need from the venue?",
        "Very little. For guest portraits she needs a banquet-size table and two chairs, and setup "
        "only takes about 10 minutes. For a bigger couple's painting she brings her own easel and "
        "carries everything with her.",
    ),
    (
        80,
        "What makes Karla's work unique?",
        "Karla works to capture each person's resemblance in a detailed and caring way, using "
        "light, color and emotion so each portrait stands out.",
    ),
    (
        90,
        "What are the welcome signs?",
        "Welcome signs double as a unique, handmade wedding guestbook. Karla paints the two of you "
        "from a photo from your engagement shoot (or another photo you choose), and guests sign "
        "around the painting. Every sign includes a frame, your date and your names. Pricing is "
        "quoted individually, so use the booking form or email Karla.",
    ),
    (
        100,
        "Do you do custom commissions or pet portraits?",
        "Yes. Karla paints custom watercolor portraits in her studio, such as couples, families and "
        "special moments, as well as pet portraits. You can browse the In-Studio Commissions and "
        "Pet Portrait galleries. Pricing depends on the piece, so use the booking form (mention "
        "it's a commission) or email Karla for a quote.",
    ),
    (
        110,
        "Do you paint at events other than weddings?",
        "Yes. Besides weddings, Karla paints at birthdays, corporate events and other celebrations. "
        "Describe your event in the booking form and she'll follow up with details.",
    ),
    (
        120,
        "How do I book or check if my date is available?",
        "Booking takes three steps:\n"
        "1. Fill out the online booking form (Book Your Date).\n"
        "2. Read and sign the contract agreement.\n"
        "3. Send the deposit to save your date.\n"
        "Karla checks availability herself and reaches out after you submit the form. Dates fill "
        "quickly, so it's best to inquire early.",
    ),
    (
        130,
        "How much is the deposit, and when is the balance due?",
        "A 50% down payment is required to reserve your date. The remaining balance is due 30 days "
        "before the event.",
    ),
    (
        140,
        "Who owns the artwork? Can we use images of it?",
        "All artwork is the sole property of Karla Lubbert and is held under copyright, even after "
        "purchase. Images and artwork may not be copied or used for personal or professional gain "
        "without Karla's written permission.",
    ),
    (
        150,
        "Are prints available?",
        "Yes. All prints are available upon request. Email Karla about the piece you'd like.",
    ),
    (
        160,
        "How can I contact Karla or see more of her work?",
        "Email Karla at WatercolorsbyKarla@gmail.com, or use the Book Your Date form for event "
        "inquiries. Her latest work is on Instagram (@watercolorsbykarla), TikTok "
        "(@watercolors.bykarla) and her Etsy shop (Karlawatercolors). Reviews from past couples "
        "are on the Reviews page.",
    ),
]

# Common questions the site doesn't answer yet. They show up in the admin
# under "Questions to answer" so Karla can fill them in.
QUESTIONS_TO_ANSWER = [
    "How much do welcome signs cost?",
    "How much do in-studio commissions and pet portraits cost, and how long do they take?",
    "What is the travel fee for events in Phoenix, Scottsdale or Tucson?",
    "What size are the guest portraits?",
    "How far in advance should we book?",
    "When do the mailed portraits arrive after the event?",
    "Can we add extra hours to a package?",
]


def _normalize(text):
    text = re.sub(r"[^\w\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", text).strip()[:500]


def seed(apps, schema_editor):
    FAQ = apps.get_model("chatbot", "FAQ")
    UnansweredQuestion = apps.get_model("chatbot", "UnansweredQuestion")
    if not FAQ.objects.exists():
        FAQ.objects.bulk_create(
            FAQ(sort_order=order, question=question, answer=answer)
            for order, question, answer in FAQS
        )
    if not UnansweredQuestion.objects.exists():
        UnansweredQuestion.objects.bulk_create(
            # times_asked=0: suggestions to fill in, not questions a visitor has asked yet.
            UnansweredQuestion(question=question, normalized=_normalize(question), times_asked=0)
            for question in QUESTIONS_TO_ANSWER
        )


def unseed(apps, schema_editor):
    FAQ = apps.get_model("chatbot", "FAQ")
    UnansweredQuestion = apps.get_model("chatbot", "UnansweredQuestion")
    FAQ.objects.filter(question__in=[q for _, q, _ in FAQS]).delete()
    UnansweredQuestion.objects.filter(
        question__in=QUESTIONS_TO_ANSWER, conversation__isnull=True
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
