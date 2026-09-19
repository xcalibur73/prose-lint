"""Unit tests for Gutenberg block comment transpiler and KSES entity protection."""

import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from prose_lint.gutenberg import markdown_to_gutenberg


class TestGutenberg(unittest.TestCase):
    def test_heading_transpilation(self):
        md = "## Core Architecture Principles"
        out = markdown_to_gutenberg(md)
        self.assertIn('<!-- wp:heading {"level":2} -->', out)
        self.assertIn('<h2 class="wp-block-heading">Core Architecture Principles</h2>', out)
        self.assertIn("<!-- /wp:heading -->", out)

    def test_paragraph_and_inline_formatting(self):
        md = "This is a **critical** test with a [link](https://example.com) and `inline_code`."
        out = markdown_to_gutenberg(md)
        self.assertIn("<!-- wp:paragraph -->", out)
        self.assertIn("<strong>critical</strong>", out)
        self.assertIn('<a href="https://example.com">link</a>', out)
        self.assertIn("<code>inline_code</code>", out)
        self.assertIn("<!-- /wp:paragraph -->", out)

    def test_list_transpilation(self):
        md = "- First item\n- Second item\n- Third item"
        out = markdown_to_gutenberg(md)
        self.assertIn("<!-- wp:list -->", out)
        self.assertIn("<ul>", out)
        self.assertIn("<li>First item</li>", out)
        self.assertIn("<!-- /wp:list -->", out)

    def test_table_transpilation(self):
        md = (
            "| Tool | Status |\n"
            "| --- | --- |\n"
            "| ProseLint | Active |\n"
            "| SchemaGraph | Verified |"
        )
        out = markdown_to_gutenberg(md)
        self.assertIn("<!-- wp:table -->", out)
        self.assertIn('<figure class="wp-block-table">', out)
        self.assertIn("<th>Tool</th>", out)
        self.assertIn("<td>ProseLint</td>", out)
        self.assertIn("<!-- /wp:table -->", out)

    def test_code_block_kses_ampersand_neutralization(self):
        md = "```javascript\nif (a && b) { return true; }\n```"
        out = markdown_to_gutenberg(md)
        self.assertIn("<!-- wp:code -->", out)
        self.assertNotIn("&&", out)  # Must neutralize raw && to protect against &#038;&#038;
        self.assertIn("/* and */", out)
        self.assertIn("<!-- /wp:code -->", out)

    def test_heading_normalization(self):
        from prose_lint.gutenberg import normalize_headings
        md = "# Top Level\n\n#### Deeply Nested Gap"
        normalized = normalize_headings(md)
        self.assertEqual(normalized, "# Top Level\n\n## Deeply Nested Gap")

        # Test multiple H1 normalization
        md_multi_h1 = "# Main Heading\n\n# Second Main Heading"
        normalized_multi = normalize_headings(md_multi_h1)
        self.assertEqual(normalized_multi, "# Main Heading\n\n## Second Main Heading")

        # Test within markdown_to_gutenberg
        out = markdown_to_gutenberg(md, normalize_heading_hierarchy=True)
        self.assertIn('<!-- wp:heading {"level":2} -->', out)
        self.assertIn('<h2 class="wp-block-heading">Deeply Nested Gap</h2>', out)


if __name__ == "__main__":
    unittest.main()
