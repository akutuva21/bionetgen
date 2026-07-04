import re

with open('tests/test_network_generator.cpp', 'r') as f:
    content = f.read()

# We can see the second `parseCheckIso behaves correctly` block is from line 380 onwards.
# Let's rename the second one to `parseCheckIso behaves correctly (duplicate)` temporarily,
# or actually we should just rename it to something unique or delete it if it's identical.
content = content.replace('TEST_CASE("parseCheckIso behaves correctly", "[NetworkGenerator]") {', 'TEST_CASE("parseCheckIso behaves correctly 2", "[NetworkGenerator]") {')
# To only rename the second one, we do this:
content = content.replace('TEST_CASE("parseCheckIso behaves correctly 2", "[NetworkGenerator]") {', 'TEST_CASE("parseCheckIso behaves correctly", "[NetworkGenerator]") {', 1)

with open('tests/test_network_generator.cpp', 'w') as f:
    f.write(content)
