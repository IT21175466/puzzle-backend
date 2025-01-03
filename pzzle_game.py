# Import necessary libraries
from flask import Flask, request, jsonify 
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Dynamic Difficulty Adjustment
class DifficultyAdjustmentModel:
    def __init__(self):
        # Possible split values (divisible by 2)
        self.split_count = [1, 2, 3, 4, 5, 6]
        self.success_threshold = 0.80  # Threshold for successful difficulty adjustment
        self.failure_threshold = 0.30  # Threshold for unsuccessful difficulty adjustment

    def adjust_difficulty(self, correct_moves, wrong_moves, current_split_count):
        """
        Adjusts the difficulty level based on performance metrics.
        """
        # Calculate the success rate
        success_rate = correct_moves / (correct_moves + wrong_moves)

        # Based on success rate and other factors, decide difficulty adjustment
        if success_rate >= self.success_threshold:
            # Player is performing well, increase difficulty (split more)
            new_split = self._increase_difficulty(current_split_count)
        elif success_rate <= self.failure_threshold:
            # Player is struggling, decrease difficulty (split less)
            new_split = self._decrease_difficulty(current_split_count)
        else:
            # Keep the difficulty the same
            new_split = self._decrease_difficulty(current_split_count)

        return new_split

    def _increase_difficulty(self, current_split_count):
        """
        Increase difficulty by selecting the next higher split value that is divisible by 2.
        """
        next_split = next((split for split in self.split_count if split > current_split_count), None)
        if next_split:
            return next_split
        return current_split_count  # If no higher split, keep the same

    def _decrease_difficulty(self, current_split_count):
        """
        Decrease difficulty by selecting the next lower split value that is divisible by 2.
        """
        prev_split = next((split for split in reversed(self.split_count) if split < current_split_count), None)
        if prev_split:
            return prev_split
        return current_split_count  # If no lower split, keep the same


# Initialize RL Model
rl_model = DifficultyAdjustmentModel()


# Define API endpoint for adjusting difficulty
@app.route("/adjust-difficulty", methods=["POST"])
def adjust_difficulty():
    try:
        # Get the request data (Performance metrics)
        data = request.get_json()

        # Extract values
        correct_moves = data.get('correct_moves', 0)
        wrong_moves = data.get('wrong_moves', 0)
        current_split_count = data.get('current_split_count', 1)

        new_split = rl_model.adjust_difficulty(correct_moves, wrong_moves, current_split_count)

        # Determine the difficulty level based on the new split count
        if new_split < 3:
            difficulty = "Low"
        elif 3 <= new_split < 5:
            difficulty = "Medium"
        else:
            difficulty = "Hard"

        # Return response with new split and difficulty level
        return jsonify({"new_split_count": new_split, "difficulty": difficulty}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Run Flask app normally (no ngrok needed)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
