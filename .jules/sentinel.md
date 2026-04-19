## 2024-05-24 - Fix XXE in BNGXML parsers
**Vulnerability:** XML External Entity (XXE) vulnerability in `lxml.etree.parse` where the parser resolves external entities by default. Attackers can provide malicious XMLs leading to arbitrary file disclosure or SSRF.
**Learning:** Always harden `lxml.etree` parsers, especially when dealing with external model definitions like SBML/BNG XML.
**Prevention:** Use `parser = etree.XMLParser(resolve_entities=False)` explicitly when invoking `etree.parse()`. Update mocked tests to reflect the new keyword argument using `parser=unittest.mock.ANY`.
