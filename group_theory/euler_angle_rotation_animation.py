import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# --- Configuration ---
# You can change the Euler angles here (in degrees)
alpha_deg = 60  # Yaw (Z-axis rotation)
beta_deg = 45   # Pitch (Y-axis rotation)
gamma_deg = 80  # Roll (X-axis rotation)

# Convert angles to radians for calculations
alpha = np.deg2rad(alpha_deg)
beta = np.deg2rad(beta_deg)
gamma = np.deg2rad(gamma_deg)

# Animation settings for a "nice and slow" feel
frames_per_rotation = 100 # Frames for each of the 3 rotations
total_frames = 3 * frames_per_rotation
interval = 40  # Delay between frames in milliseconds

# --- Rotation Matrix Functions ---
def rotation_matrix_x(theta):
    """Returns the rotation matrix around the X-axis."""
    return np.array([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
    ])

def rotation_matrix_y(theta):
    """Returns the rotation matrix around the Y-axis."""
    return np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

def rotation_matrix_z(theta):
    """Returns the rotation matrix around the Z-axis."""
    return np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])

# --- Plot Setup ---
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_box_aspect([1, 1, 1]) # Ensure aspect ratio is 1:1:1 for correct perspective

# Set axis limits and labels
ax.set_xlim([-1.2, 1.2])
ax.set_ylim([-1.2, 1.2])
ax.set_zlim([-1.2, 1.2])
ax.set_xlabel('X (Lab Frame)', fontsize=12)
ax.set_ylabel('Y (Lab Frame)', fontsize=12)
ax.set_zlabel('Z (Lab Frame)', fontsize=12)
ax.set_title('Euler Angle Rotation: Z(α) -> Y(β) -> X(γ)', fontsize=16, pad=20)

# --- Draw Static Lab Frame (X, Y, Z) ---
origin = np.zeros(3)
lab_frame_basis = np.eye(3)
lab_colors = ['gray', 'gray', 'gray']
lab_labels = ['X', 'Y', 'Z']
for i in range(3):
    ax.quiver(origin[0], origin[1], origin[2],
              lab_frame_basis[i, 0], lab_frame_basis[i, 1], lab_frame_basis[i, 2],
              color=lab_colors[i], linestyle='--', arrow_length_ratio=0.1)
    ax.text(lab_frame_basis[i, 0] * 1.1, lab_frame_basis[i, 1] * 1.1, lab_frame_basis[i, 2] * 1.1,
            f'${lab_labels[i]}$', color=lab_colors[i], fontsize=14)

# --- Initialize Animated Object Frame (x', y', z') ---
object_basis = np.eye(3)
obj_colors = ['#d62728', '#2ca02c', '#1f77b4'] # Red, Green, Blue
obj_labels = ["x'", "y'", "z'"]
quivers = [ax.quiver(origin[0], origin[1], origin[2],
                     object_basis[i, 0], object_basis[i, 1], object_basis[i, 2],
                     color=obj_colors[i], arrow_length_ratio=0.1, label=f'Object {obj_labels[i]}') for i in range(3)]
texts = [ax.text(object_basis[i, 0] * 1.1, object_basis[i, 1] * 1.1, object_basis[i, 2] * 1.1,
                 f"${obj_labels[i]}$", color=obj_colors[i], fontsize=14) for i in range(3)]

# On-screen text for current angles
angle_text = ax.text2D(0.02, 0.85, '', transform=ax.transAxes, fontsize=12,
                       bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

# --- Animation Update Function ---
def update(frame):
    """This function is called for each frame of the animation."""
    # Stage 1: Rotate around Lab Z-axis by alpha
    if frame < frames_per_rotation:
        progress = frame / frames_per_rotation
        current_alpha = alpha * progress
        R = rotation_matrix_z(current_alpha)
        stage_info = f'Stage 1: Yaw about Z-axis\n$\\alpha$ = {np.rad2deg(current_alpha):.1f}°'

    # Stage 2: Rotate around Lab Y-axis by beta
    elif frame < 2 * frames_per_rotation:
        progress = (frame - frames_per_rotation) / frames_per_rotation
        current_beta = beta * progress
        # Apply Y-rotation to the result of the Z-rotation
        R = rotation_matrix_y(current_beta) @ rotation_matrix_z(alpha)
        stage_info = f'Stage 2: Pitch about Y-axis\n$\\alpha$ = {alpha_deg:.1f}°, $\\beta$ = {np.rad2deg(current_beta):.1f}°'

    # Stage 3: Rotate around Lab X-axis by gamma
    else:
        progress = (frame - 2 * frames_per_rotation) / frames_per_rotation
        current_gamma = gamma * progress
        # Apply X-rotation to the result of the previous two rotations
        R_z_alpha = rotation_matrix_z(alpha)
        R_y_beta = rotation_matrix_y(beta)
        R = rotation_matrix_x(current_gamma) @ R_y_beta @ R_z_alpha
        stage_info = f'Stage 3: Roll about X-axis\n$\\alpha$ = {alpha_deg:.1f}°, $\\beta$ = {beta_deg:.1f}°, $\\gamma$ = {np.rad2deg(current_gamma):.1f}°'

    # Calculate the new orientation of the object frame's basis vectors
    new_basis = R @ np.eye(3)

    # Update the quiver arrows for the object frame
    for i, q in enumerate(quivers):
        q.set_segments([np.array([origin, new_basis[:, i]]).T])

    # Update the position of the object frame labels (x', y', z')
    for i, t in enumerate(texts):
        t.set_position((new_basis[0, i] * 1.1, new_basis[1, i] * 1.1))
        t.set_z(new_basis[2, i] * 1.1)

    # Update the angle display text
    angle_text.set_text(stage_info)

    # Return the artists that were modified
    return quivers + texts + [angle_text]

# --- Create and Display Animation ---
# Create the animation object. blit=False is recommended for 3D plots.
ani = FuncAnimation(fig, update, frames=total_frames,
                    interval=interval, blit=False, repeat=True)

ax.legend(loc='upper right')
plt.show()

# To save the animation as a video file (requires ffmpeg):
# print("Saving animation... this may take a moment.")
# ani.save('euler_rotation_animation.mp4', writer='ffmpeg', fps=30)
# print("Animation saved as euler_rotation_animation.mp4")
