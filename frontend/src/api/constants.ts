/**
 * Shared constants for the Real Estate Market Intelligence dashboard.
 */

// Strict color map for all 10 models to prevent semantic collisions
// Success (#16A34A), Warning (#D97706), and Danger (#DC2626) colors are excluded.
export const MODEL_COLORS: Record<string, string> = {
  linear_regression: "#64748B",         // Slate
  ridge_regression: "#3B82F6",          // Blue
  lasso_regression: "#0284C7",          // Sky
  random_forest_regression: "#1E3A8A",  // Deep Blue (Primary)
  xgboost_regression: "#0D9488",        // Teal (Secondary)
  decision_tree_regression: "#06B6D4",   // Cyan (Non-status: warning replaced)
  logistic_classification: "#4F46E5",    // Indigo (Non-status: success replaced)
  svm_classification: "#8B5CF6",         // Purple
  naive_bayes_text: "#EC4899",           // Pink
  knn_retrieval: "#9F1239",              // Deep Burgundy
};

// Friendly display names for each model ID
export const MODEL_NAMES: Record<string, string> = {
  linear_regression: "Linear Regression",
  ridge_regression: "Ridge Regression",
  lasso_regression: "Lasso Regression",
  random_forest_regression: "Random Forest Regressor",
  xgboost_regression: "XGBoost Regressor (Production)",
  decision_tree_regression: "Decision Tree Explainer",
  logistic_classification: "Logistic Regression Classifier",
  svm_classification: "SVM Price Tier Classifier",
  naive_bayes_text: "Naive Bayes Description Classifier",
  knn_retrieval: "KNN Similar Retrieval",
};

// Distinct list of 28 unique neighborhoods present in the Ames Housing database
export const AMES_NEIGHBORHOODS = [
  "Blmngtn",
  "Blueste",
  "BrDale",
  "BrkSide",
  "ClearCr",
  "CollgCr",
  "Crawfor",
  "Edwards",
  "Gilbert",
  "Greens",
  "GrnHill",
  "IDOTRR",
  "Landmrk",
  "MeadowV",
  "Mitchel",
  "NAmes",
  "NPkVill",
  "NWAmes",
  "NoRidge",
  "NridgHt",
  "OldTown",
  "SWISU",
  "Sawyer",
  "SawyerW",
  "Somerst",
  "StoneBr",
  "Timber",
  "Veenker",
] as const;
