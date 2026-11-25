import random

# STUDENT
IN_GRADE = 90.0
IN_STRIKES = 0

# TA
IN_TRUST = 55
IN_RAPPORT = 50

# INSTRUCTOR
IN_DEAN = 55
IN_STUDENTS = 55
IN_COLLEAGUES = 55

MAX_STAT = 100

LABELS = {
    "grade": "Course grade",
    "strikes": "Integrity strikes",
    "trust": "Instructor trust",
    "rapport": "Student rapport",
    "dean": "Dean approval",
    "students": "Student satisfaction",
    "colleagues": "Colleague satisfaction",
}


# MAIN MENU
def get_menu_choice():
    while True:
        try:
            choice = int(input(
                "\n[ MAIN MENU ]\n\n"
                "Choose your character:\n\n"
                "1. Instructor - Leff Jucas\n"
                "2. Teaching Assistant - Wessica Jeaver\n"
                "3. Student - Peanne Jark\n\n"
                "Enter your choice: "
            ))

            if choice in [1, 2, 3]:
                return choice
            else:
                print("\nInvalid menu choice. Try again.")

        except ValueError:
            print("\nMust be a number.")

def coin_flip():
    coin = random.randint(1, 2)
    return coin

def load_events(filename):
    events = []

    with open(filename, "r") as infile:
        for line in infile:
            if line.strip():
                events.append(line.strip().split("#"))

    random.shuffle(events)

    return events


# DISPLAY FUNCTIONS
def display_instr(dean, students, colleagues):
    print("\n=== INSTRUCTOR - LEFF JUCAS ===\n")
    print("WIN: Get promoted to UA PRESIDENT (Dean approval 75+, student satisfaction 65+, colleague satisfaction 65+)")
    print("LOSE: Get FIRED (any of the three scores hits 0)")
    print(f"Dean approval: {dean}\t\tStudent satisfaction: {students}\t\tColleague satisfaction: {colleagues}\n")

def display_ta(trust, rapport):
    print("\n=== TEACHING ASSISTANT - WESSICA JEAVER ===\n")
    print("WIN: Get promoted to LEAD TA(Instructor trust 65+, student rapport 60+)")
    print("LOSE: Get FIRED (trust or rapport hits 0)")
    print(f"\nInstructor trust: {trust}\t\tStudent rapport: {rapport}\n")


def display_student(grade, strikes):
    print("\n=== STUDENT - PEANNE JARK ===\n")
    print("WIN: Finish MIS 221 with an A+ (97 or higher)")
    print("LOSE: Get suspended/expelled (3 strikes)")
    print(f"\nGrade: {grade}\t\tStrikes: {strikes}/3\n")

def get_event_answer():
    answer = input("Your choice (a/b): ").lower().strip()

    while answer not in ["a", "b"]:
        answer = input("Invalid input. Try again: ").lower().strip()

    return answer

def play_student(event, score, strikes):
    print(f"\n{event[0]}")
    print(f"a) {event[1]}")
    print(f"b) {event[2]}")

    answer = get_event_answer()

    coin = coin_flip()

    if answer == "a":
        if coin == 1:
            index = 3
        else:
            index = 6
    else:
        if coin == 1:
            index = 9
        else:
            index = 12

    print("\n" + event[index])

    score += int(event[index + 1])
    strikes += int(event[index + 2])

    score = min(MAX_STAT, score)

    return score, strikes

def play_ta(event, trust, rapport):
    print(f"\n{event[0]}")
    print(f"a) {event[1]}")
    print(f"b) {event[2]}")

    answer = get_event_answer()

    coin = coin_flip()

    if answer == "a":
        if coin == 1:
            index = 3
        else:
            index = 6
    else:
        if coin == 1:
            index = 9
        else:
            index = 12

    print("\n" + event[index])

    trust += int(event[index + 1])
    rapport += int(event[index + 2])

    trust = min(MAX_STAT, trust)
    rapport = min(MAX_STAT, rapport)

    return trust, rapport


# INSTRUCTOR EVENTS
def play_instr(event, dean, students, colleagues):
    print(f"\n{event[0]}")
    print(f"a) {event[1]}")
    print(f"b) {event[2]}")

    answer = get_event_answer()

    coin = coin_flip()

    if answer == "a":
        if coin == 1:
            index = 3
        else:
            index = 7
    else:
        if coin == 1:
            index = 11
        else:
            index = 15

    print("\n" + event[index])

    dean += int(event[index + 1])
    students += int(event[index + 2])
    colleagues += int(event[index + 3])

    dean = min(MAX_STAT, dean)
    students = min(MAX_STAT, students)
    colleagues = min(MAX_STAT, colleagues)

    return dean, students, colleagues

def student_game():
    score = IN_GRADE
    strikes = IN_STRIKES

    display_student(score, strikes)

    quiz = []

    with open("quiz.txt", "r") as infile:
        for line in infile:
            if line.strip():
                quiz.append(line.strip().split("#"))

    events = load_events("student_events.txt")

    for i in range(max(len(quiz), len(events))):

        if score >= 97 or strikes >= 3:
            break

        if i < len(quiz):
            question = quiz[i]

            print(f"\n{question[0]}")
            print(f"a) {question[1]}")
            print(f"b) {question[2]}")
            print(f"c) {question[3]}")
            print(f"d) {question[4]}")

            answer = input("Your answer (a/b/c/d): ").lower().strip()

            while answer not in ["a", "b", "c", "d"]:
                answer = input("Invalid input. Try again: ").lower().strip()

            if answer == question[5].lower().strip():
                print("Correct! +1 point")
                score += 1
            else:
                print(f"Incorrect. The answer was {question[5]}. -2 points")
                score -= 2

            print(f"Current score: {score}")

        if score >= 97 or strikes >= 3:
            break

        # STUDENT EVENT
        if i < len(events):
            score, strikes = play_student(events[i], score, strikes)

            print(f"\nCurrent score: {score}\t\tCurrent strikes: {strikes}/3")

    # GAME RESULT
    if strikes >= 3:
        print("\nYou've been expelled! GAME OVER")

    elif score >= 97:
        print("\nYou made an A+ in MIS 221! VICTORY")

    else:
        print("\nGAME OVER! You didn't reach an A+.")
        print("\n[ FINAL REPORT ]\n")
        print(f"Grade: {score}\t\tStrikes: {strikes}/3")


def ta_game():
    trust = IN_TRUST
    rapport = IN_RAPPORT

    display_ta(trust, rapport)

    events = load_events("ta_events.txt")

    for event in events:

        if (trust >= 65 and rapport >= 60) or trust <= 0 or rapport <= 0:
            break

        trust, rapport = play_ta(event, trust, rapport)

        print(f"\nInstructor trust: {trust}\t\tStudent rapport: {rapport}")

    if trust <= 0 or rapport <= 0:
        print("\nYou've been FIRED! GAME OVER")

    elif trust >= 65 and rapport >= 60:
        print("\nYou've been promoted to LEAD TA! VICTORY")

    else:
        print("\nGAME OVER! You didn't reach your promotion goals.")
    print("\n[ FINAL REPORT ]\n") 
    print(f"Instructor trust: {trust}\t\tStudent rapport: {rapport}")

def instr_game():
    dean = IN_DEAN
    students = IN_STUDENTS
    colleagues = IN_COLLEAGUES

    display_instr(dean, students, colleagues)

    events = load_events("instr_events.txt")

    for event in events:

        if (dean >= 75 and students >= 65 and colleagues >= 65):
            break

        if dean <= 0 or students <= 0 or colleagues <= 0:
            break

        dean, students, colleagues = play_instr(
            event, dean, students, colleagues
        )

        print(f"\nDean approval: {dean}\t\tStudent satisfaction: {students}\t\tColleague satisfaction: {colleagues}")

    if dean <= 0 or students <= 0 or colleagues <= 0:
        print("\nYou've been FIRED! GAME OVER")

    elif dean >= 75 and students >= 65 and colleagues >= 65:
        print("\nYou've been promoted to UA PRESIDENT! VICTORY")

    else:
        print("\nGAME OVER! You didn't reach your promotion goals.")
    print("\n[ FINAL REPORT ]\n") 
    print(f"Dean approval: {dean}\t\tStudent satisfaction: {students}\t\tColleague satisfaction: {colleagues}")

#MAIN FLOW

def route_em(menu_choice):

    if menu_choice == 1:
        instr_game()

    elif menu_choice == 2:
        ta_game()

    elif menu_choice == 3:
        student_game()

print("\n=== CHOOSE YOUR MIS 221 JOURNEY ===")
menu_choice = get_menu_choice()
route_em(menu_choice)

print("\nThanks for playing! Roll Tide.")

# fortune cookie
print()
print("=== TODAY'S FORTUNE ===\n")
print("Happiness is a choice you make every day.\nYOUR LUCKY NUMBERS: 12, 56, 27, 55, 32, 8\n")