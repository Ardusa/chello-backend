from transformers import pipeline

# # Initialize the zero-shot classifier
# classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-roberta-base")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Specific Thresholds
SPECIAL_THRESHOLD = 0.984
SUPER_SPECIAL_THRESHOLD = 0.95


print()


# Function to detect dependencies
def detect_dependencies(tasks: dict, threshold: float=0.95, dependencies: dict=None) -> dict[str, str]:
    """
    Detects dependencies between tasks based on sentence similarity.

    :param tasks: Dictionary where keys are task names and values are task descriptions.
    :param threshold: Similarity score threshold for determining dependencies.
    :return: Dictionary mapping each task to its detected dependencies.
    """
    
    if dependencies is None:
        dependencies = {task_id: [] for task_id in tasks.keys()}

    for task_A, description_A in tasks.items():
        for task_B, description_B in tasks.items():                
            if (task_A in dependencies[task_B] or task_B in dependencies[task_A] or task_A == task_B):
                continue

            # hypotheses1 = [
            #     f"{task_A} must be completed after {task_B}.",
            #     f"{task_A} cannot start until {task_B} is finished.",
            #     f"{task_A} is dependent on the completion of {task_B}.",
            #     f"Finish {task_B} before starting {task_A}.",
            #     f"{task_A} is blocked until {task_B} is completed.",
            #     f"{task_A} follows {task_B} in the development sequence.",
            #     f"{task_A} requires {task_B} to be finished first.",
            #     f"Before beginning {task_A}, {task_B} must be completed.",
            #     f"{task_A} is part of the pipeline and comes after {task_B}.",
            #     f"{task_B} is a prerequisite for {task_A}.",
            #     f"{task_A} is scheduled after {task_B} in the workflow.",
            #     f"{task_A} cannot be tested until {task_B} is done."
            # ]
            
            # hypotheses2 = [
            #     f"{task_B} must be completed before {task_A} starts.",
            #     f"{task_B} is a prerequisite for {task_A}.",
            #     f"{task_B} enables {task_A}.",
            #     f"Complete {task_B} to unlock {task_A}.",
            #     f"{task_B} is a required step before {task_A}.",
            #     f"{task_A} follows {task_B} in the pipeline.",
            #     f"{task_A} depends on the success of {task_B}.",
            #     f"{task_A} relies on {task_B} being finalized.",
            #     f"{task_B} ensures {task_A} can proceed.",
            #     f"Before {task_A}, {task_B} must be fully implemented."
            # ]

            # all_developments = [
            #     f"{task_A} must be completed after all development tasks are finished.",
            #     f"Do not start {task_A} until all prior tasks are completed.",
            #     f"{task_A} is the final step after all tasks are implemented.",
            #     f"Before beginning {task_A}, ensure all tasks are finalized.",
            #     f"{task_A} requires the entire development cycle to be completed first."
            # ]
            
            # all_modules = [
            #     f"{task_A} depends on the successful completion of all modules.",
            #     f"{task_A} cannot proceed until all modules are implemented.",
            #     f"All modules must be completed before {task_A} starts.",
            #     f"{task_A} follows the completion of all necessary modules.",
            #     f"{task_A} is scheduled after all major components are integrated."
            # ]


            # Hypotheses for A relying on B        
            hypotheses1 = [
                f"Start {task_A} after the {task_B} is finished.",
                f"Work on {task_A} after completing the {task_B}.",
                f"Ensure {task_A} is done after the {task_B} is finalized.",
                f"Begin {task_A} only after the {task_B} is completed.",
                f"Proceed with {task_A} after the {task_B} is functional.",
                f"Implement {task_A} when the {task_B} is done.",
                f"Execute {task_A} after finishing the {task_B}.",
                f"Develop {task_A} after achieving {task_B}'s goals.",
                f"Focus on {task_A} after wrapping up {task_B}.",
                f"Ensure {task_A} starts after the completion of {task_B}.",
                f"Finalize {task_A} only after completing the {task_B}.",
                f"Launch {task_A} once the {task_B} is operational.",
                f"Work on {task_A} after successfully completing the {task_B}.",
                f"Wait until the {task_B} is finished before starting {task_A}.",
                f"Postpone {task_A} until the {task_B} is ready.",
                f"Do not begin {task_A} until the {task_B} is functional.",
                f"Complete {task_A} following the {task_B}.",
                f"Start {task_A} as soon as the {task_B} is done.",
                f"Continue to {task_A} after completing the {task_B}.",
                f"Only begin {task_A} once the {task_B} has been finalized.",
                f"Begin {task_A} after resolving {task_B} requirements.",
                f"Proceed with {task_A} once the {task_B} has been successfully completed.",
                f"Postpone {task_A} until the {task_B} reaches completion.",
                f"Ensure {task_A} follows the completion of the {task_B}.",
                f"Execute {task_A} only after finishing the {task_B}.",
                f"Start working on {task_A} only after {task_B} is finalized.",
                f"Ensure {task_A} is dependent on the finalization of {task_B}.",
                f"Delay {task_A} until the {task_B} is fully operational.",
                f"Start {task_A} after confirming the success of the {task_B}.",
                f"Ensure {task_A} begins when {task_B} has been completed.",
                f"Allow {task_A} to commence once the {task_B} is finalized.",
                f"Set {task_A} to follow after the successful execution of {task_B}.",
                f"Ensure {task_A} starts only when the {task_B} goals are met.",
                f"Postpone {task_A} to ensure {task_B} is completed first.",
                f"Make sure {task_A} aligns with the completion of {task_B}.",
                f"Plan {task_A} for after the {task_B} concludes.",
                f"Start {task_A} following the resolution of {task_B}.",
                f"Execute {task_A} only once the {task_B} is resolved.",
                f"Ensure {task_A} is carried out after {task_B} is accomplished.",
                f"Perform {task_A} after all {task_B} are completed.",
                f"Complete {task_A} after all {task_B} tasks are finished.",
                f"Perform {task_A} once all {task_B} tasks are completed.",
                f"Do not start {task_A} until all {task_B} tasks are done."
            ]

            # Hypotheses for B relying on A
            hypotheses2 = [
                f"Complete {task_A} before starting the {task_B}.",
                f"Work on {task_A} prior to {task_B}.",
                f"Ensure {task_A} is done before the {task_B} can proceed.",
                f"Start {task_A} earlier than the {task_B}.",
                f"Finish {task_A} before {task_B} begins.",
                f"Develop {task_A} as a prerequisite to {task_B}.",
                f"Focus on {task_A} before considering the {task_B}.",
                f"Complete {task_A} so the {task_B} can start.",
                f"Implement {task_A} first, then proceed to {task_B}.",
                f"Prioritize {task_A} to enable the {task_B}.",
                f"Ensure {task_A} is finalized before starting the {task_B}.",
                f"Begin {task_A} well before {task_B} can proceed.",
                f"Prepare {task_A} as a necessary step for the {task_B}.",
                f"Complete {task_A} to unlock progress on the {task_B}.",
                f"Do not proceed with {task_B} until {task_A} is complete.",
                f"Work on {task_A} as a requirement for {task_B}.",
                f"Complete {task_A} ahead of the {task_B} schedule.",
                f"Ensure {task_A} readiness before the {task_B} is initiated.",
                f"Finalize {task_A} as a critical step preceding {task_B}.",
                f"Wrap up {task_A} before {task_B} begins.",
                f"Achieve completion of {task_A} to set up {task_B}.",
                f"Make {task_A} the first priority to unblock {task_B}.",
                f"Focus on finishing {task_A} so that {task_B} can start.",
                f"Complete {task_A} to ensure a smooth start for {task_B}.",
                f"Plan {task_A} to precede the {task_B}.",
                f"Ensure {task_A} is the foundation for the {task_B}.",
                f"Prepare {task_A} as a key enabler of {task_B}.",
                f"Complete {task_A} as an essential condition for {task_B}.",
                f"Work on {task_A} as a necessary precursor to {task_B}.",
                f"Focus on completing {task_A} to support the {task_B}.",
                f"Ensure {task_A} readiness well before {task_B} can begin.",
                f"Achieve {task_A} milestones to unlock {task_B} progress.",
                f"Ensure {task_A} is finalized ahead of the {task_B} deadline."
            ]
            
            all_developments = [
                f"Perform {task_A} after all development tasks are completed."]
                # f"Do not start {task_A} until all development tasks are done.",
                # f"Ensure {task_A} is done after all other development tasks are completed."
            # ]
            
            all_modules = [
                # f"{task_A} depends on the successful completion of all modules.",
                f"Perform {task_A} after all modules are constructed."
            ]


            # Result of A relying on B
            result1 = classifier(
                description_A,
                candidate_labels=hypotheses1,
                multi_label=True
            )
            
            # Result of B relying on A
            result2 = classifier(
                description_A,
                candidate_labels=hypotheses2,
                multi_label=True
            )
            
            all_dev_results = classifier(
                description_A,
                candidate_labels=all_developments,
                multi_label=False
            )
            
            all_mod_results = classifier(
                description_A,
                candidate_labels=all_modules,
                multi_label=False
            )
            
            # Get the maximum score for each result
            appliedResult1 = result1['scores'][0]
            appliedResult2 = result2['scores'][0]
            
            appliedResult_all_dev = all_dev_results['scores'][0]
            appliedResult_all_mod = all_mod_results['scores'][0]
            
            appliedResultAllTasks = max(appliedResult_all_dev, appliedResult_all_mod)
            dev_task = True if (appliedResultAllTasks == appliedResult_all_dev) else False

            # Print the dependency being tested along with the max score and the hypotheses that the score was achieved with
            print(f"Testing dependency: {task_A} -> {task_B}")
            print(f"Max score for {task_A} depending on {task_B}: {appliedResult1} with hypothesis: {result1['labels'][0]}")
            print(f"Max score for {task_B} depending on {task_A}: {appliedResult2} with hypothesis: {result2['labels'][0]}")
            print(f"Max score for {task_A} depending on all {"development tasks" if dev_task else "modules"} : {appliedResultAllTasks} with hypothesis: {all_dev_results['labels'][0] if dev_task else all_mod_results['labels'][0]}")
            
            # Standard dependencies
            if appliedResult1 > appliedResult2 and appliedResult1 > threshold:
                dependencies[task_A].append(task_B)

            if appliedResult2 > appliedResult1 and appliedResult2 > threshold:
                dependencies[task_B].append(task_A)

            skip = False

            if appliedResultAllTasks > SPECIAL_THRESHOLD:
                for potential_task_id in tasks.keys():

                    score = classifier(potential_task_id, candidate_labels=("development" if dev_task else "module"), multi_label=True)['scores'][0]
                    print(f"Testing special case dependency: {task_A} -> {potential_task_id}")
                    print(f"Max score for {potential_task_id} being a {"development" if dev_task else "module"} : {score}\n")

                    if potential_task_id != task_A and score > SUPER_SPECIAL_THRESHOLD:
                    # if potential_task_id != task_A and ("development" in potential_task_id.lower() or "module" in potential_task_id.lower()):
                        dependencies[task_A].append(potential_task_id)
                        skip = True

            print()
            if (skip):
                break

    return dependencies
