# Function validates user input
# If user input is valid, returns user input
# else it will raise ValueError and keep prompting user for correct input
def validate_option(question, valid_inputs):
    while True:
        try:
            user_input = input(question).strip()

            if len(user_input) == 0:
                raise ValueError("Player did not enter an input. Please choose an option\n")
            elif user_input.isdigit():
                user_input = int(user_input)
                if user_input in valid_inputs:
                    return user_input
                else:
                    raise ValueError(f"Please select an option from {min(valid_inputs)} to {max(valid_inputs)}\n")
            else:
                raise ValueError("Invalid option, please enter a valid option\n")
        except ValueError as e:
            print(e)


# Validates user input for moving the hero in the map
def validate_move(question):
    while True:
        try:
            user_input = input(question).strip().upper()

            if len(user_input) == 0:
                raise ValueError("Player did not enter an input. Please enter a direction\n")
            
            elif len(user_input) > 1:
                raise ValueError("Invalid direction. Please enter a valid direction\n")
                
            elif user_input.isalpha():
                if user_input in ["W", "A", "S", "D"]:
                    return user_input
                else:
                    raise ValueError("Invalid direction. Please enter a valid direction\n")
        
        except ValueError as e:
            print(e)
