# 0001. Use Sphinx For Markup

**Status:** Proposed
**Date:** 2026-09-02
**Deciders:** Dennis, Ashlyn

## Context

The project needs a documentation site that can be maintained by students and faculty who are not web developers.

The site has three fixed requirements:

1. Content must be authored in a lightweight markup language, specifically Markdown or reStructuredText. Adding or editing a page must not require writing raw HTML, CSS, or JavaScript.
2. The site must build automatically through GitHub Actions when changes are pushed to the default branch. There must be no manual build-and-upload process.
3. The site must publish through GitHub Pages.

There are two documentation sites involved in the project. The existing course site uses Sphinx. The existing user manual uses Jekyll. The two sites will cross-link heavily.

The project therefore needs to choose a documentation generator that satisfies the three fixed requirements while also considering how students will author content, how the two sites will work together, and the cost of changing an existing site.

## Options considered

### Option A: Sphinx

Use Sphinx as the documentation generator. Content can be written in reStructuredText or Markdown through the MyST extension. GitHub Actions will build the documentation and publish it to GitHub Pages.

**Hard constraints:** Satisfies all three hard constraints: lightweight markup, GitHub Actions builds, and GitHub Pages publishing.

* Pro: Matches the existing course site.
* Pro: Designed for structured technical documentation.
* Pro: Supports reStructuredText and Markdown through MyST.
* Pro: Allows the two documentation sites to use the same generator.
* Con: reStructuredText is less familiar to most students than Markdown.
* Con: The existing Jekyll user manual will require migration if both sites are standardised on Sphinx.
* Con: Contributors may need some Sphinx-specific knowledge.

### Option B: Jekyll

Use Jekyll as the documentation generator with Markdown source files. GitHub Actions will build the site and GitHub Pages will host the result.

**Hard constraints:** Satisfies all three hard constraints: lightweight markup, GitHub Actions builds, and GitHub Pages publishing.

* Pro: Markdown is familiar to most students.
* Pro: The existing user manual already uses Jekyll.
* Pro: Jekyll works naturally with GitHub Pages.
* Con: Does not match the existing course site's Sphinx setup.
* Con: The project would either continue maintaining two different documentation systems or require migrating the course site to Jekyll.
* Con: Standardising the course site on Jekyll would require migration work on existing course documentation.

### Option C: MkDocs with Material

Use MkDocs with the Material theme. Documentation will be written in Markdown, built with GitHub Actions, and published to GitHub Pages.

**Hard constraints:** Satisfies all three hard constraints: lightweight markup, GitHub Actions builds, and GitHub Pages publishing.

* Pro: Markdown is familiar to most students.
* Pro: Quick to configure for documentation.
* Pro: Material provides documentation features such as search and navigation.
* Con: Introduces a third documentation generator into the project.
* Con: Does not match either the existing Sphinx course site or the existing Jekyll user manual.
* Con: Both existing sites would remain on different generators unless additional migration work is performed.

### Option D: Standardise both sites on one generator

Migrate both the course site and user manual to a single documentation generator, then use that generator for future documentation.

**Hard constraints:** This option can satisfy all three hard constraints when the selected generator is configured to use lightweight markup, GitHub Actions, and GitHub Pages.

* Pro: Both sites would use the same documentation workflow.
* Pro: Students and faculty would only need to learn one documentation system.
* Pro: Cross-linking and maintenance between the two sites would be more consistent.
* Con: Requires migration of existing documentation.
* Con: Existing content and configuration would need to be converted and tested.
* Con: Migration adds work before new documentation can be delivered.
* Con: The choice of which generator to standardise on would still need to be made.

## Decision

We chose **Option A: Sphinx**.

The project will use **Sphinx as the documentation generator**, with lightweight markup as the source format. Markdown can be used through MyST where it is more productive for contributors.

The **course site should continue using Sphinx**, and the **user manual should move toward Sphinx** rather than maintaining two different documentation generators. This gives the two sites a common documentation system while allowing them to remain separate sites where appropriate.

Sphinx was selected because it already matches the course site's existing documentation system and is designed for structured technical documentation. The ability to use Markdown through MyST also reduces the barrier for students who are more familiar with Markdown.

The migration cost is real. The existing Jekyll user manual will need to be converted to Sphinx if the two sites are to be standardised. Existing pages, configuration, navigation, links, and the build process will need to be checked after migration. This work is accepted because maintaining one documentation generator is preferable to introducing a third tool or continuing with two different systems.

The site will be built automatically through GitHub Actions and published to GitHub Pages.

## Consequences

**Easier now:**

* The project uses the same documentation generator as the existing course site.
* Students and faculty can edit documentation using lightweight markup.
* Markdown can be used through MyST.
* Both sites can use the same documentation tooling.
* The build and publishing process can be automated through GitHub Actions and GitHub Pages.

**Harder now:**

* Contributors who are unfamiliar with Sphinx may need to learn its conventions.
* reStructuredText is less familiar to many students than Markdown.
* The existing Jekyll user manual will require migration work.
* Existing documentation must be tested after migration to ensure links, navigation, formatting, and builds continue to work.

**We are committed to:**

* Using Sphinx as the documentation generator.
* Keeping documentation source in Markdown or reStructuredText rather than raw HTML, CSS, or JavaScript.
* Keeping the course site on Sphinx.
* Moving the user manual toward Sphinx so both sites use the same generator.
* Building automatically with GitHub Actions on pushes to the default branch.
* Publishing through GitHub Pages.
* Making the documentation maintainable by students and faculty who are not web developers.

**We should revisit this if:**

* Sphinx becomes a significant barrier to students or faculty contributing documentation.
* The Sphinx build cannot be reliably automated through GitHub Actions.
* GitHub Pages is no longer an available or suitable publishing platform.
* The migration from Jekyll proves substantially more costly than expected.
* The requirements of either documentation site change enough that using different generators becomes more practical.
