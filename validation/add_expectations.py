import great_expectations as gx

print("=" * 60)
print("Adding Expectations")
print("=" * 60)

# ---------------------------------------------------
# Context
# ---------------------------------------------------

context = gx.get_context(project_root_dir="gx")

# ---------------------------------------------------
# Datasource
# ---------------------------------------------------

datasource = context.data_sources.get("athlete_datasource")

asset = datasource.get_asset("athlete_dataset")

batch_definition = asset.get_batch_definition("athlete_batch")

batch = batch_definition.get_batch()

# ---------------------------------------------------
# Expectation Suite
# ---------------------------------------------------

suite = context.suites.get("athlete_suite")

validator = batch.get_validator(
    expectation_suite=suite
)

# ===================================================
# EXPECTATIONS
# ===================================================

validator.expect_column_to_exist("Athlete_ID")

validator.expect_column_values_to_not_be_null("Athlete_ID")

validator.expect_column_values_to_be_unique("Athlete_ID")

validator.expect_column_values_to_be_between(
    "Age",
    min_value=18,
    max_value=60
)

validator.expect_column_values_to_be_between(
    "Recovery_Score",
    min_value=0,
    max_value=100
)

validator.expect_column_values_to_be_in_set(
    "Gender",
    ["Male", "Female"]
)

validator.expect_column_values_to_be_between(
    "Sleep_Duration_Hours",
    min_value=0,
    max_value=24
)

validator.expect_column_values_to_be_between(
    "Mood_Score",
    min_value=1,
    max_value=10
)

validator.expect_column_values_to_be_between(
    "Energy_Level",
    min_value=1,
    max_value=10
)

validator.expect_column_values_to_be_between(
    "Training_Duration_Min",
    min_value=1,
    max_value=300
)

validator.save_expectation_suite()

print("\n=======================================")
print("10 Expectations Added Successfully!")
print("=======================================")