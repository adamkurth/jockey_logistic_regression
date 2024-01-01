import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from logistic import RaceModel

# Define constants
num_horses = 10
num_laps = 3
race_dist = num_laps * 2 * np.pi  # 2pi * radius

# logit model
race_model = RaceModel(num_horses)

# Assumption: each hprse has base speed, vary closely to the mean.
base_speed = 0.015 # for all horses
variation = 0.0005 # small variations
horse_speeds = np.abs(np.random.normal(loc=base_speed, scale=variation, size=num_horses)) # positive
horse_positions = np.zeros(num_horses)

# animation
fig_race, ax_race = plt.subplots()
ax_race.set_xlim(-1.5, 1.5)
ax_race.set_ylim(-1, 1)
ax_race.set_aspect('equal')  # ensure no distortion

fig_leaderboard, ax_leaderboard = plt.subplots()
ax_leaderboard.axis('off')


colors = plt.cm.rainbow(np.linspace(0, 1, num_horses))
points = [ax_race.plot([], [], 'o', color=colors[i])[0] for i in range(num_horses)]
leaderboard_texts = [ax_leaderboard.text(0.5, 0.95 - 0.05 * i, '', verticalalignment='top', horizontalalignment='center') for i in range(num_horses)]

def track(angle):
    """Calculate the x,y coordinates for an angle on the track"""
    a = 1.0 # semi-major axis (x-radius)
    b = 0.5 # semi-minor axis (y-radius)
    return a * np.cos(angle), b * np.sin(angle)

def init():
    """Initialize the animation"""
    for point in points:
        point.set_data([], [])
    return points

def update(frame):
    global horse_positions, horse_speeds

    # Check if the leading horse has completed the number of laps
    leading_horse_dist = np.max(horse_positions)
    if leading_horse_dist >= race_dist:
        # Freeze the frames by returning the current state without updating positions or probabilities
        for txt in leaderboard_texts:
            txt.set_text(txt.get_text())  # Freeze leaderboard texts
        return points + leaderboard_texts
    
    horse_positions = (horse_positions + horse_speeds) % (2 * np.pi)

    # Update the race model and predict probabilities
    race_model.update_model(horse_positions, horse_speeds)
    probabilities = race_model.predict_probabilities()

    sorted_indices = np.argsort(-probabilities[:, 1])
    for i, idx in enumerate(sorted_indices):
        prob = probabilities[idx, 1] if probabilities is not None else "N/A"
        leaderboard_texts[i].set_text(f"Rank {i+1}: Horse {idx} - {prob:.4f}")
        leaderboard_texts[i].set_color(colors[idx])

    for i, point in enumerate(points):
        x, y = track(horse_positions[i])
        point.set_data([x], [y])

    fig_leaderboard.canvas.draw()

    if np.max(horse_positions) >= race_dist:
        plt.close('all')

    return points


ani = FuncAnimation(fig_race, update, frames=np.linspace(0, race_dist, 1200), init_func=init, blit=True, interval=10)
plt.show()