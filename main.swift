// import CoreML

// func detectDependencies(from tasks: [String: String]) -> [String] {
//     // Load the Core ML model
//     guard let model = try? DependencyDetector(configuration: MLModelConfiguration()) else {
//         print("Failed to load the model.")
//         return []
//     }

//     // Create an MLDictionaryFeatureProvider with the tasks dictionary
//     let input = try? MLDictionaryFeatureProvider(dictionary: tasks)

//     // Perform prediction
//     guard let output = try? model.prediction(from: input!) else {
//         print("Prediction failed.")
//         return []
//     }

//     // Process the output to extract dependencies
//     // This will depend on the specific output format of your model
//     let dependencies = output.featureValue(for: "dependencies")?.stringValue ?? ""
//     return dependencies.split(separator: ",").map { String($0) }
// }
