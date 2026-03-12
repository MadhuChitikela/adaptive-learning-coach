import math


def irt_probability(ability: float, difficulty: float,
                    discrimination: float = 1.0,
                    guessing: float = 0.25) -> float:
    """
    3-Parameter IRT Model — same used in GRE/GMAT
    Returns probability of correct answer (0-1)
    """
    exponent = discrimination * (ability - difficulty)
    prob = guessing + (1 - guessing) / (1 + math.exp(-exponent))
    return prob


def update_ability(current_ability: float, correct: bool,
                   difficulty: float) -> float:
    """
    Updates student ability estimate after each answer.
    Correct answer → ability goes up
    Wrong answer   → ability goes down
    """
    learning_rate = 0.3

    prob = irt_probability(current_ability, difficulty)

    if correct:
        delta = learning_rate * (1 - prob)
    else:
        delta = -learning_rate * prob

    # Keep ability between -3 and 3
    new_ability = max(-3.0, min(3.0, current_ability + delta))
    return round(new_ability, 3)


def get_next_difficulty(ability: float) -> float:
    """
    Returns optimal difficulty for next question.
    Targets questions where student has ~60% chance of success.
    """
    # Target difficulty slightly above current ability
    target = ability + 0.2
    return round(max(-2.0, min(2.0, target)), 2)


def ability_to_level(ability: float) -> str:
    """Converts ability score to human readable level"""
    if ability >= 2.0:   return "Expert 🏆"
    elif ability >= 1.0: return "Advanced ⭐"
    elif ability >= 0.0: return "Intermediate 📈"
    elif ability >= -1.0: return "Beginner 📚"
    else:                return "Novice 🌱"


def ability_to_score(ability: float) -> float:
    """Converts IRT ability (-3 to 3) to percentage (0-100)"""
    return round((ability + 3) / 6 * 100, 1)


if __name__ == "__main__":
    ability = 0.0
    print("🧪 IRT Algorithm Test")
    print(f"Starting ability: {ability} ({ability_to_level(ability)})")

    answers = [True, True, False, True, False, True, True, True]
    for i, correct in enumerate(answers):
        diff = get_next_difficulty(ability)
        ability = update_ability(ability, correct, diff)
        score = ability_to_score(ability)
        print(f"Q{i+1}: {'✅' if correct else '❌'} | Difficulty: {diff} | Ability: {ability} | Score: {score}%")

    print(f"\nFinal Level: {ability_to_level(ability)}")
