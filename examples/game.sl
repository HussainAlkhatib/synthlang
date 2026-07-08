# Simple text-based game
# Number guessing game

fn guess_game(): int
    secret = 42
    let attempts = 0
    print("Guess the number (1-100):")
    
    while attempts < 10:
        let guess = 50
        attempts = attempts + 1
        if guess == secret:
            print("Correct! You win!")
            return attempts
        elif guess < secret:
            print("Too low!")
        else:
            print("Too high!")
    
    print("Game over! The number was:", secret)
    return -1

guess_game()