import re

with open('tests/test_network_generator.cpp', 'r') as f:
    content = f.read()

content = content.replace('TEST_CASE("parsePrintRules behaves correctly", "[NetworkGenerator]") {', 'TEST_CASE("parsePrintRules behaves correctly 2", "[NetworkGenerator]") {')
content = content.replace('TEST_CASE("parsePrintRules behaves correctly 2", "[NetworkGenerator]") {', 'TEST_CASE("parsePrintRules behaves correctly", "[NetworkGenerator]") {', 1)

with open('tests/test_network_generator.cpp', 'w') as f:
    f.write(content)
