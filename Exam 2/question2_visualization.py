import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Set up for high quality output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# Data
deaths_15to49 = np.array([58013, 875097, 1030000, 1982, 66611, 153915, 411733, 134059,
   49458, 49879, 21526, 49514, 231907, 260425, 129070, 265315, 151607, 74900,
   23810, 24606, 1409, 16668, 206354, 654651, 511219, 519490])

deaths_50to69 = np.array([81604, 3960000, 5150000, 138261, 55601, 239089, 884065, 48849,
    44799, 25105, 18340, 38186, 142613, 62402, 402277, 592200, 405835, 71239,
   1963, 28344, 36931, 19151, 1000000, 311714, 213121, 429672])

# Create figure
fig, ax = plt.subplots(figsize=(13, 10))

# Set background
fig.patch.set_facecolor('#fafbfc')
ax.set_facecolor('#fafbfc')

# Key causes - ordered by story (increases on top, decreases on bottom)
key_causes = [
    # Causes that DECREASE with age (shown in blue)
    ("Homicide", 260425, 62402),
    ("Drowning", 134059, 48849),
    ("Road accidents", 654651, 311714),
    ("Suicide", 511219, 213121),
    ("HIV/AIDS", 231907, 142613),
    # Causes that INCREASE with age (shown in red)
    ("Kidney disease", 129070, 402277),
    ("Respiratory disease", 206354, 1000000),
    ("Cancers", 875097, 3960000),
    ("Cardiovascular disease", 1030000, 5150000),
]

n_causes = len(key_causes)
y_positions = np.arange(n_causes)
scale = 1_000_000
bar_height = 0.32
gap = 0.08

# Colors
color_decrease = '#2980b9'  # Blue
color_increase = '#c0392b'  # Red

# Draw bars
for i, (cause, d15, d50) in enumerate(key_causes):
    ratio = d50 / d15

    # Choose color based on category
    color = color_decrease if i < 5 else color_increase

    # Young age group (15-49) - lighter, positioned above
    ax.barh(i + bar_height/2 + gap/2, d15/scale, height=bar_height,
            color=color, alpha=0.35, edgecolor=color, linewidth=0.8)

    # Older age group (50-69) - darker, positioned below
    ax.barh(i - bar_height/2 - gap/2, d50/scale, height=bar_height,
            color=color, alpha=0.85, edgecolor=color, linewidth=0.8)

    # Format value labels
    if d15 >= 1_000_000:
        label_15 = f'{d15/1_000_000:.1f}M'
    else:
        label_15 = f'{d15/1000:.0f}K'

    if d50 >= 1_000_000:
        label_50 = f'{d50/1_000_000:.1f}M'
    else:
        label_50 = f'{d50/1000:.0f}K'

    # Position labels at end of bars
    ax.text(d15/scale + 0.06, i + bar_height/2 + gap/2, label_15,
            ha='left', va='center', fontsize=9, color='#777')
    ax.text(d50/scale + 0.06, i - bar_height/2 - gap/2, label_50,
            ha='left', va='center', fontsize=9, color='#444', fontweight='medium')

# Add cause labels on left with more space
ax.set_yticks(y_positions)
ax.set_yticklabels([c[0] for c in key_causes], fontsize=11, fontweight='medium')

# Add ratio annotations on right edge
for i, (cause, d15, d50) in enumerate(key_causes):
    ratio = d50 / d15
    color = color_decrease if i < 5 else color_increase

    if ratio >= 1:
        label = f'×{ratio:.1f}'
    else:
        label = f'÷{1/ratio:.1f}'

    ax.text(5.8, i, label, fontsize=11, fontweight='bold',
            color=color, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor=color, alpha=0.8, linewidth=1.5))

# Column header for ratios
ax.text(5.8, n_causes + 0.3, 'CHANGE', fontsize=10, fontweight='bold',
        color='#555', ha='center', va='bottom')

# Styling
ax.set_xlim(0, 6.3)
ax.set_ylim(-0.8, n_causes + 0.5)
ax.set_xlabel('Deaths (millions)', fontsize=12, fontweight='medium', labelpad=12)

# Add dividing line between categories
ax.axhline(y=4.5, color='#aaa', linestyle='--', linewidth=1.5, alpha=0.7)

# Category labels in left margin area using figure coordinates
fig.text(0.03, 0.32, 'DECREASES\nwith age', fontsize=12, color=color_decrease,
         fontweight='bold', ha='center', va='center', rotation=90)
fig.text(0.03, 0.70, 'INCREASES\nwith age', fontsize=12, color=color_increase,
         fontweight='bold', ha='center', va='center', rotation=90)

# Add arrow indicators
ax.annotate('', xy=(0.15, 8.7), xytext=(0.15, 5.2),
            arrowprops=dict(arrowstyle='->', color=color_increase, lw=2.5))
ax.annotate('', xy=(0.15, 0.3), xytext=(0.15, 4.0),
            arrowprops=dict(arrowstyle='->', color=color_decrease, lw=2.5))

# Legend - positioned clearly
legend_elements = [
    mpatches.Patch(facecolor='gray', alpha=0.35, edgecolor='gray',
                   linewidth=0.8, label='Ages 15–49'),
    mpatches.Patch(facecolor='gray', alpha=0.85, edgecolor='gray',
                   linewidth=0.8, label='Ages 50–69'),
]
leg = ax.legend(handles=legend_elements, loc='lower right', frameon=True,
                fancybox=True, shadow=False, fontsize=11, framealpha=0.95,
                edgecolor='#ccc')

# Title and subtitle
fig.suptitle('How Causes of Death Shift as We Age',
             fontsize=20, fontweight='bold', y=0.97, x=0.5, color='#2c3e50')
ax.set_title('Chronic diseases surge dramatically while violence and accidents decline',
             fontsize=12, color='#666', style='italic', pad=20, loc='center')

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#bbb')

# Tick styling
ax.tick_params(axis='y', length=0, pad=10)
ax.tick_params(axis='x', colors='#666')

# Source note
fig.text(0.5, 0.015, 'Data: Worldwide deaths by cause (representative sample, one year)',
         fontsize=9, color='#999', style='italic', ha='center')

plt.tight_layout(rect=[0.06, 0.03, 0.98, 0.93])
plt.savefig('/home/claude/death_causes_visualization.png',
            dpi=300, bbox_inches='tight', facecolor='#fafbfc', edgecolor='none')
plt.savefig('/home/claude/death_causes_visualization.pdf',
            dpi=300, bbox_inches='tight', facecolor='#fafbfc', edgecolor='none')
print("Saved successfully!")
