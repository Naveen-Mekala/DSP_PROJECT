import great_expectations as gx

print("=" * 60)
print("ATHLETE RECOVERY DATA VALIDATION")
print("=" * 60)

# --------------------------------------------------
# Load Great Expectations Context
# --------------------------------------------------

context = gx.get_context(project_root_dir="gx")

# --------------------------------------------------
# Load Datasource
# --------------------------------------------------

datasource = context.data_sources.get("athlete_datasource")

# --------------------------------------------------
# Load Asset
# --------------------------------------------------

asset = datasource.get_asset("athlete_dataset")

# --------------------------------------------------
# Load Batch
# --------------------------------------------------

batch_definition = asset.get_batch_definition("athlete_batch")

batch = batch_definition.get_batch()

# --------------------------------------------------
# Load Expectation Suite
# --------------------------------------------------

suite = context.suites.get("athlete_suite")

# --------------------------------------------------
# Create Validator
# --------------------------------------------------

validator = batch._create_validator(result_format="SUMMARY")

print("\nRunning Validation...\n")

# --------------------------------------------------
# Validate
# --------------------------------------------------

results = validator.validate_expectation_suite(suite)

# --------------------------------------------------
# Summary
# --------------------------------------------------

stats = results.statistics

print("=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

print(f"Total Expectations : {stats['evaluated_expectations']}")
print(f"Passed             : {stats['successful_expectations']}")
print(f"Failed             : {stats['unsuccessful_expectations']}")
print(f"Success Percentage : {stats['success_percent']}%")

print("\n" + "=" * 60)
print("FAILED EXPECTATIONS")
print("=" * 60)

failed = False

for result in results.results:
    if not result.success:
        failed = True
        print(f"\n❌ {result.expectation_config.type}")

        if "column" in result.expectation_config.kwargs:
            print(f"Column : {result.expectation_config.kwargs['column']}")

        if hasattr(result, "result") and result.result:
            if "unexpected_count" in result.result:
                print(f"Unexpected Count : {result.result['unexpected_count']}")

            if "unexpected_percent" in result.result:
                print(
                    f"Unexpected Percent : {round(result.result['unexpected_percent'],2)}%"
                )

if not failed:
    print("✅ All Expectations Passed!")

print("\n" + "=" * 60)
print("VALIDATION COMPLETED")
print("=" * 60)