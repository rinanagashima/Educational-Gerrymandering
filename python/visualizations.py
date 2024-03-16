import matplotlib.pyplot as plt
import os


def plot_all(blocks, district, schools, sabs, leaid, state_figures_dir):
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
    plt.savefig(os.path.join(state_figures_dir, f'{leaid}_allcensusblocks.png'))

    # plot
    plt.show()
    
    # Create a plot of the sabs to make sure it loaded properly
    sabs.plot()
    plt.axis('off')

    # save as png file
    plt.savefig(os.path.join(state_figures_dir, f'{leaid}_sabs.png'))

    # plot
    plt.show()
    
    # Convert all column names to lowercase
    schools.columns = schools.columns.str.lower()
    # Create a plot of the schools to make sure it loaded properly
    schools.plot()
    plt.axis('off')
    plt.show()

    return
