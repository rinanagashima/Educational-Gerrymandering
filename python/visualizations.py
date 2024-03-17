import matplotlib.pyplot as plt
import os
import numpy as np


def plot_all(blocks, district, schools, sabs, leaid, state_output_dir):
    # plot to make sure the census blocks are being mapped onto the school district properly
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the district as the base layer
    district.plot(ax=ax, color='lightblue', edgecolor='black')

    # Overlay the filtered Arizona census blocks within the selected district
    blocks.plot(ax=ax, color='red', alpha=0.5)

    # Customization
    ax.set_title('Census Blocks within Selected District')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # save as png file
    plt.savefig(os.path.join(state_output_dir, f'{leaid}_allcensusblocks.png'))

    # plot
    plt.show()
    
    # Create a plot of the sabs to make sure it loaded properly
    sabs.plot()
    plt.axis('off')

    # save as png file
    plt.savefig(os.path.join(state_output_dir, f'{leaid}_sabs.png'))

    # plot
    plt.show()
    
    # Convert all column names to lowercase
    schools.columns = schools.columns.str.lower()
    # Create a plot of the schools to make sure it loaded properly
    schools.plot()
    plt.axis('off')
    plt.show()

    return

def plot_stackedbar(apportioned_students):
    apportioned_students.drop('total', axis=1).plot(kind='bar', stacked=True, figsize=(10, 6), legend=True)
    plt.title('Apportioned Students by Race Across Blocks (Non-Zero Populations Only)')
    plt.xlabel('Census Block')
    plt.ylabel('Number of Students')
    # set x-axis tick labels to an empty list to reduce visual clutter
    plt.xticks(ticks=[], labels=[])
    # plot
    plt.show()

    return

def plot_histogram(data, initial_dissim_shannon, state_abbrev, state_output_dir, leaid):
    # Determine the bins for the histogram
    count, bins, ignored = plt.hist(data, bins=10, alpha=0.75, color='blue', edgecolor='black', label='All Results')

    # Find the bin that contains the 'initial_dissim_shannon'
    bin_width = bins[1] - bins[0]
    initial_bin = np.digitize(initial_dissim_shannon, bins) - 1  # Find the bin index, adjust by 1 due to 0-indexing

    # Highlight the bin containing 'initial_dissim_shannon'
    plt.bar(bins[initial_bin] + bin_width/2, count[initial_bin], width=bin_width, color='darkblue', edgecolor='black', label='Initial Dissimilarity')

    # Add titles and labels
    plt.title(f'Ensemble of plans in {state_abbrev} using short bursts')
    plt.xlabel('Dissimilarity Score')
    plt.ylabel('Frequency')
    plt.legend()
    
    # save as png file
    plt.savefig(os.path.join(state_output_dir, f'{leaid}_histogram.png'))

    # Show plot
    plt.show()
    return