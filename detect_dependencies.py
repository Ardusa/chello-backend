from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import constants

# Load primary sentence transformer model for similarity detection
similarity_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Load secondary model for dependency classification (text classification)
dependency_classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
# dependency_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Dependency Indicators
A_TO_B_INDICATORS = {"after", "once", "following", "subsequent", "then"}
B_TO_A_INDICATORS = {"before", "prior", "previous", "preceding", "earlier"}

# Labels for dependency classification
DEPENDENCY_LABELS = ["dependency", "independent", "sequence", "requirement"]

# Function to detect dependencies
def detect_dependencies(tasks: dict, dependencies: dict = None) -> dict:
    """
    Detects dependencies between tasks based on their descriptions using similarity and text classification models.
    
    :param tasks: Dictionary where keys are task IDs and values are task descriptions.
    :param dependencies: Dictionary where keys are task IDs and values are lists of dependent task IDs.
    :return: Dictionary where keys are task IDs and values are lists of dependent task IDs.
    """
    
    if dependencies is None:
        dependencies = {task_id: set() for task_id in tasks.keys()}  # Use sets to avoid duplicate dependencies

    task_list = list(tasks.keys())
    descriptions = list(tasks.values())

    for i, task_A in enumerate(task_list):
        for j, task_B in enumerate(task_list):
            if task_A == task_B:
                continue

            # Define hypotheses for dependency detection in both directions
            hypothesis_A_B = f"Complete {task_A} before completing {task_B}."
            hypothesis_B_A = f"Complete {task_B} before completing {task_A}."

            # Compute similarity scores in both directions
            similarity_A_B = util.pytorch_cos_sim(
                similarity_model.encode(descriptions[i], convert_to_tensor=True),
                similarity_model.encode(hypothesis_A_B, convert_to_tensor=True)
            ).item()

            similarity_B_A = util.pytorch_cos_sim(
                similarity_model.encode(descriptions[j], convert_to_tensor=True),
                similarity_model.encode(hypothesis_B_A, convert_to_tensor=True)
            ).item()

            # Verify dependency classification using the secondary model
            dependency_check_A_B = dependency_classifier(descriptions[i], candidate_labels=DEPENDENCY_LABELS, multi_label=True)
            dependency_check_B_A = dependency_classifier(descriptions[j], candidate_labels=DEPENDENCY_LABELS, multi_label=True)

            # Extract confidence scores
            is_dependency_A_B = dependency_check_A_B["scores"][0] > constants.WEAK_THRESHOLD  # Confidence threshold
            is_dependency_B_A = dependency_check_B_A["scores"][0] > constants.WEAK_THRESHOLD  # Confidence threshold

            # Check for strong dependencies
            if similarity_A_B > similarity_B_A and similarity_A_B >= constants.STRONG_THRESHOLD:
                dependencies[task_A].add(task_B)
                print(f"✅ Strong Dependency: {task_A} → {task_B} (Similarity: {similarity_A_B:.4f})")
            elif similarity_B_A > similarity_A_B and similarity_B_A >= constants.STRONG_THRESHOLD:
                dependencies[task_B].add(task_A)
                print(f"✅ Strong Dependency: {task_B} → {task_A} (Similarity: {similarity_B_A:.4f})")
            # Check for weak dependencies using both indicators and secondary model verification
            elif (
                similarity_A_B > similarity_B_A and similarity_A_B >= constants.WEAK_THRESHOLD and 
                any(ind in descriptions[i].lower() for ind in A_TO_B_INDICATORS) and is_dependency_A_B
            ):
                dependencies[task_A].add(task_B)
                print(f"⚠️ Weak Dependency: {task_A} → {task_B} (Similarity: {similarity_A_B:.4f})")
            elif (
                similarity_B_A > similarity_A_B and similarity_B_A >= constants.WEAK_THRESHOLD and 
                any(ind in descriptions[j].lower() for ind in B_TO_A_INDICATORS) and is_dependency_B_A
            ):
                dependencies[task_B].add(task_A)
                print(f"⚠️ Weak Dependency: {task_B} → {task_A} (Similarity: {similarity_B_A:.4f})")
            else:
                print(f"❌ No dependency: {task_A} → {task_B} (Similarity: {similarity_A_B:.4f})")

    # Remove indirect dependencies (transitive reduction)
    for task in list(dependencies.keys()):
        direct_deps = dependencies[task].copy()
        for dep in direct_deps:
            if dep in dependencies:
                dependencies[task] -= dependencies[dep]  # Remove transitive dependencies
                
                # Organize dependencies so that tasks with no dependencies are listed first
                sorted_tasks = sorted(dependencies.keys(), key=lambda task: len(dependencies[task]))
                organized_dependencies = {task: dependencies[task] for task in sorted_tasks}
                dependencies.clear()
                dependencies.update(organized_dependencies)
                
                # Ensure that tasks with dependencies are listed after their dependencies
                for task in list(dependencies.keys()):
                    for dep in dependencies[task]:
                        if dep in dependencies and task in dependencies[dep]:
                            dependencies[dep].remove(task)
                            dependencies[task].add(dep)

    # Convert sets back to lists for consistency
    return {task: list(deps) for task, deps in dependencies.items()}