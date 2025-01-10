import os
import networkx as nx
import matplotlib.pyplot as plt
import constants


def generate_DAG(dependencies: dict, title="dag.png", durations: dict = None):
    """
    Generates a DAG from the dependencies dictionary and saves it as a PNG file.

    :param dependencies: Dictionary where keys are tasks and values are lists of dependent tasks.
    :param title: Filename to save the DAG image (default: "dag.png").
    :param durations: Dictionary where keys are tasks and values are estimated durations (optional).
    """
    
    # Define the full path for saving
    save_path = os.path.join(constants.DAG_PATH, title + constants.DAG_EXTENSION)

    # Ensure the directory exists
    os.makedirs(constants.DAG_PATH, exist_ok=True)

    # Create a directed graph
    G = nx.DiGraph()

    # Add edges from dependencies
    for task, deps in dependencies.items():
        for dep in deps:
            G.add_edge(dep, task)  # Directed edge from dependency to dependent task

    # Draw the graph
    num_tasks = len(dependencies)
    plt.figure(
        figsize=(
            num_tasks * constants.DAG_NODE_MULTIPLIER,
            num_tasks * constants.DAG_NODE_MULTIPLIER,
        ),
        facecolor="gray",
    )

    # pos = nx.spring_layout(G, seed=42, k=2.0)  # Layout for consistent positioning and increased spacing
    # pos = nx.shell_layout(G)  # Layout for consistent positioning and increased spacing

    # Dont really need dist its kind of useless but keep the logic around
    if durations:
        dist = {
            task: {t: duration for t in dependencies.keys()}
            for task, duration in durations.items()
        }
    else:
        dist = None  # noqa: F841

    # Layout for consistent positioning and increased spacing
    pos = nx.kamada_kawai_layout(G)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=6000,
        node_color="#FF6347",
        edge_color="gray",
        font_size=10,
        font_weight="bold",
        arrowsize=60,
        node_shape="d",
        alpha=1,
        label=title,
        bbox=dict(
            facecolor="skyblue", edgecolor="black", boxstyle="round,pad=0.6", alpha=0.7
        ),
        connectionstyle="arc3,rad=0.2",
    )
    plt.margins(0.05)  # Add padding to the edges of the whole picture

    # Save the figure as a PNG file
    plt.savefig(save_path, format="png")
    plt.close()  # Close the plot to prevent it from displaying

    print(f"DAG saved as {title} in {constants.DAG_PATH}")
