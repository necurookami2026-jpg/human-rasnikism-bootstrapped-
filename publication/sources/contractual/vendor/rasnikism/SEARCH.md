# Searching, matching, finding, summoning, and mathing

The implemented local search tool covers the catalogue's software families. “Mathing” is interpreted as both matching and mathematical work; “summoning” means opening a selected draft workspace. The terminology is provisional and AI-assisted.

Open search.html. Choose all-term substring matching, exact category-name matching, or approximate name matching. Case and compatibility Unicode variants are normalized. Approximate matching uses Levenshtein edit distance on category names and words, with a maximum permitted distance of one to three depending on query length. It is not semantic AI search. Results state why they matched and paginate six at a time.

Summon links use the catalogue's module fragment to select the appropriate draft workspace. They do not install applications, run processes, invoke autonomous agents, or access another system. Unknown module identifiers leave the catalogue on its normal initial selection.

The math workspace implements exact integer addition, subtraction, multiplication, integer division with remainder, and greatest common divisor. Inputs are bounded to 1000 characters. Division by zero is rejected. Negative division truncates toward zero; the remainder retains the dividend's sign. These conventions are stated in the UI.

Everything runs locally with no external search API or query upload. It is an expandable implementation, not a claim of exhaustive searching or unlimited capability. Search does not inspect the full source documents or the wider Internet. Legal and specialist category limits remain as documented in CATALOGUE.md.

Run `node software/test_search.cjs` for matching, ranking, pagination, integer arithmetic, and invalid-input checks.
