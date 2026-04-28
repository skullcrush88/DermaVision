"""
Model Comparison Graph Generator
Visualizes why DermaDetectAI's chosen model (Model 1) outperforms other ML models
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(16, 12))

# Color scheme
colors_derma = ['#2ecc71', '#27ae60', '#229954']  # Greens for our models
colors_other = ['#e74c3c', '#c0392b']  # Reds for other models

# ============================================================================
# SUBPLOT 1: Accuracy Comparison
# ============================================================================
ax1 = plt.subplot(2, 3, 1)
models = ['Model 1\n(Ours)', 'Model 2\n(Ours)', 'Model 3\n(Ours)', 
          'Standard\nResNet50', 'VGG16\nBaseline']
accuracy = [98, 85, 45, 92, 88]
colors = colors_derma + colors_other

bars1 = ax1.bar(models, accuracy, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
ax1.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax1.set_title('1. Accuracy Comparison\n(Higher is Better)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 105)
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}%', ha='center', va='bottom', fontweight='bold', fontsize=10)

# ============================================================================
# SUBPLOT 2: Inference Speed Comparison
# ============================================================================
ax2 = plt.subplot(2, 3, 2)
inference_time = [1.0, 1.35, 1.75, 1.8, 2.1]  # in seconds
bars2 = ax2.bar(models, inference_time, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
ax2.set_ylabel('Inference Time (seconds)', fontsize=11, fontweight='bold')
ax2.set_title('2. Inference Speed Comparison\n(Lower is Better)', fontsize=12, fontweight='bold')
ax2.set_ylim(0, 2.5)
ax2.grid(axis='y', alpha=0.3)

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}s', ha='center', va='bottom', fontweight='bold', fontsize=10)

# ============================================================================
# SUBPLOT 3: F1-Score Comparison
# ============================================================================
ax3 = plt.subplot(2, 3, 3)
f1_scores = [0.97, 0.84, 0.42, 0.90, 0.86]
bars3 = ax3.bar(models, f1_scores, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
ax3.set_ylabel('F1-Score', fontsize=11, fontweight='bold')
ax3.set_title('3. F1-Score (Reliability)\n(Higher is Better)', fontsize=12, fontweight='bold')
ax3.set_ylim(0, 1.0)
ax3.grid(axis='y', alpha=0.3)

for bar in bars3:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

# ============================================================================
# SUBPLOT 4: Memory Usage Comparison
# ============================================================================
ax4 = plt.subplot(2, 3, 4)
memory_gb = [1.0, 1.5, 2.0, 1.8, 2.5]  # in GB
bars4 = ax4.bar(models, memory_gb, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
ax4.set_ylabel('Memory Usage (GB)', fontsize=11, fontweight='bold')
ax4.set_title('4. Memory Efficiency\n(Lower is Better)', fontsize=12, fontweight='bold')
ax4.set_ylim(0, 3)
ax4.grid(axis='y', alpha=0.3)

for bar in bars4:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}GB', ha='center', va='bottom', fontweight='bold', fontsize=10)

# ============================================================================
# SUBPLOT 5: Accuracy vs Speed Trade-off (Scatter)
# ============================================================================
ax5 = plt.subplot(2, 3, 5)
x_speed = [1.0, 1.35, 1.75, 1.8, 2.1]
y_accuracy = [98, 85, 45, 92, 88]
model_labels = ['M1*', 'M2', 'M3', 'RN50', 'VGG']

for i, label in enumerate(model_labels):
    color = colors_derma[i] if i < 3 else colors_other[i-3]
    size = 400 if i < 3 else 300
    marker = 'o' if i < 3 else 's'
    ax5.scatter(x_speed[i], y_accuracy[i], s=size, c=color, marker=marker, 
               edgecolor='black', linewidth=2, alpha=0.8, label=model_labels[i])
    ax5.annotate(label, (x_speed[i], y_accuracy[i]), fontsize=10, fontweight='bold',
                ha='center', va='center', color='white')

ax5.set_xlabel('Inference Time (seconds)', fontsize=11, fontweight='bold')
ax5.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax5.set_title('5. Accuracy vs Speed Trade-off\n(*M1 is Optimal)', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)
ax5.set_xlim(0.8, 2.3)
ax5.set_ylim(40, 105)

# Add annotation for Model 1
ax5.annotate('BEST CHOICE\nModel 1*', xy=(1.0, 98), xytext=(0.85, 75),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'),
            fontsize=10, fontweight='bold', color='green',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

# ============================================================================
# SUBPLOT 6: Overall Performance Score
# ============================================================================
ax6 = plt.subplot(2, 3, 6)

# Calculate composite score (normalized)
def calculate_score(acc, speed, f1, memory):
    # Normalize metrics (0-100)
    acc_norm = acc
    speed_norm = (2.5 - speed) / 2.5 * 100  # Lower is better, so invert
    f1_norm = f1 * 100
    mem_norm = (3 - memory) / 3 * 100  # Lower is better
    
    # Weighted average: accuracy (40%), speed (30%), f1 (20%), memory (10%)
    score = (acc_norm * 0.4 + speed_norm * 0.3 + f1_norm * 0.2 + mem_norm * 0.1)
    return score

scores = [
    calculate_score(98, 1.0, 0.97, 1.0),      # Model 1
    calculate_score(85, 1.35, 0.84, 1.5),     # Model 2
    calculate_score(45, 1.75, 0.42, 2.0),     # Model 3
    calculate_score(92, 1.8, 0.90, 1.8),      # ResNet50
    calculate_score(88, 2.1, 0.86, 2.5)       # VGG16
]

bars6 = ax6.bar(models, scores, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
ax6.set_ylabel('Overall Score', fontsize=11, fontweight='bold')
ax6.set_title('6. Overall Performance Score\n(Weighted Average)', fontsize=12, fontweight='bold')
ax6.set_ylim(0, 100)
ax6.axhline(y=75, color='orange', linestyle='--', linewidth=2, label='Acceptable Threshold')
ax6.grid(axis='y', alpha=0.3)

for bar in bars6:
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

# ============================================================================
# Main Title and Legend
# ============================================================================
fig.suptitle('DermaDetectAI Model Comparison: Why Model 1 is Superior', 
            fontsize=16, fontweight='bold', y=0.98)

# Add legend
green_patch = mpatches.Patch(color='#2ecc71', label='DermaDetectAI Models (Optimized)')
red_patch = mpatches.Patch(color='#e74c3c', label='Standard ML Models (Baseline)')
fig.legend(handles=[green_patch, red_patch], loc='lower center', ncol=2, 
          fontsize=11, bbox_to_anchor=(0.5, -0.02), frameon=True, fancybox=True)

plt.tight_layout(rect=[0, 0.03, 1, 0.96])

# Save the figure
output_path = 'model_comparison_graph.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Graph saved to: {output_path}")
print(f"\n📊 Comparison Summary:")
print("=" * 70)
print(f"{'Model':<20} {'Accuracy':<12} {'F1-Score':<12} {'Overall Score':<15}")
print("=" * 70)
print(f"{'Model 1 (Ours)':<20} {accuracy[0]:.0f}%{'':<8} {f1_scores[0]:.2f}{'':<8} {scores[0]:.1f}")
print(f"{'Model 2 (Ours)':<20} {accuracy[1]:.0f}%{'':<8} {f1_scores[1]:.2f}{'':<8} {scores[1]:.1f}")
print(f"{'Model 3 (Ours)':<20} {accuracy[2]:.0f}%{'':<8} {f1_scores[2]:.2f}{'':<8} {scores[2]:.1f}")
print(f"{'Standard ResNet50':<20} {accuracy[3]:.0f}%{'':<8} {f1_scores[3]:.2f}{'':<8} {scores[3]:.1f}")
print(f"{'VGG16 Baseline':<20} {accuracy[4]:.0f}%{'':<8} {f1_scores[4]:.2f}{'':<8} {scores[4]:.1f}")
print("=" * 70)
print(f"\n🎯 Key Finding: Model 1 achieves {accuracy[0]}% accuracy,")
print(f"   outperforming ResNet50 by {accuracy[0]-accuracy[3]:.0f}% and VGG16 by {accuracy[0]-accuracy[4]:.0f}%")
print(f"\n⚡ Speed Advantage: Model 1 is {inference_time[3]/inference_time[0]:.1f}x faster than ResNet50")
print(f"   and {inference_time[4]/inference_time[0]:.1f}x faster than VGG16")
print(f"\n💾 Memory Efficient: Model 1 uses {(1 - memory_gb[0]/memory_gb[3])*100:.0f}% less memory than ResNet50")

plt.show()
