import pytest
from classifier import classify_dilemma, check_crisis

TEST_CASES = [
    # J1: Fearlessness
    ("I am terrified of speaking in front of my class and everyone laughing", 1),
    ("Major exam fear and anxiety making me freeze", 1),

    # J2: Self-Faith
    ("I feel like an imposter and a fraud, I am not good enough", 2),
    ("Deep insecurity that I have no talent and will fail", 2),

    # J3: Focus (the exact prompt from your spec)
    ("I keep checking Instagram while studying and can't concentrate", 3),
    ("Mind is everywhere, doom scrolling reels instead of working", 3),

    # J4: Purpose
    ("I don't know what I'm doing with my life and feel completely lost", 4),
    ("Confused about my career path, too many options and no clear direction", 4),

    # J5: Persistence
    ("I failed my exam again and I just want to quit and give up", 5),
    ("Got rejected from 5 job interviews in a row, done trying", 5),

    # J6: Strength
    ("I am burnt out, drained, and have zero mental energy left", 6),
    ("Completely exhausted, working 14 hours and feeling mentally weak", 6),

    # J7: Self-Mastery
    ("I lose my temper over small things and can't control my anger", 7),
    ("Seeing everyone succeed on Instagram makes me jealous and bitter", 7),

    # J8: Service
    ("I achieved my goals but life feels empty and meaningless, want to help others", 8),
    ("Selfish ambition is making me feel isolated, yearning to give back to society", 8),
]

@pytest.mark.parametrize("dilemma, expected_lesson", TEST_CASES)
def test_classifier_accuracy(dilemma, expected_lesson):
    res = classify_dilemma(dilemma)
    assert res["lessonId"] == expected_lesson, (
        f"Expected Lesson {expected_lesson} for '{dilemma}', got {res['lessonId']} ({res['journey']})"
    )

def test_crisis_safety_gate():
    crisis_text = "I want to end my life, there is no point living"
    assert check_crisis(crisis_text) is True
    res = classify_dilemma(crisis_text)
    assert res["isCrisis"] is True

def test_prompt_from_user_spec():
    """Specific acceptance test from prompt: Instagram while studying -> Focus."""
    res = classify_dilemma("I keep checking Instagram while studying and can't concentrate.")
    assert res["lessonId"] == 3
    assert res["journey"] == "Focus"
