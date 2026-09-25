# Ground rules

Version 1.0 · approved by the author · changes only with the author's approval (§6).

Every automated check and every reviewer finding cites a rule number from this file, for
example `GR-2.3`. A rule that nothing enforces is marked *(review)*; the aim over time is to
turn review-only rules into automated checks (§5.3).

## §1 Independence and confidentiality

- **GR-1.1** Nothing in the repository or on the site may identify the author's employer or its
  internal work: company, group, product, platform, project, team or people names, internal
  codes, customers, or internal figures. *(check: deny-list · review: confidentiality)*
- **GR-1.2** The private source library is used as a source of experience only. It is never
  quoted, copied, or paraphrased closely enough to be recognised. Pages read as general
  industry practice. *(review: confidentiality)*
- **GR-1.3** No internal document, excerpt, extract or research note enters the repository,
  including under ignored folders that may later be committed. *(check: path and deny-list)*
- **GR-1.4** The deny-list itself must not reveal what it protects. It is stored as hashed
  values or as a CI secret, never as plain names. *(check)*

## §2 Evidence

- **GR-2.1** Every claim beyond common knowledge is backed by a public source, in this order
  of preference:
  1. standards and frameworks (ISO, NIST, OWASP, SLSA, SAFe);
  2. research (DORA, peer-reviewed studies);
  3. recognised practitioners (martinfowler.com, Thoughtworks Technology Radar, established
     engineering blogs);
  4. official tool documentation, for facts about that tool only. *(review: accuracy)*
- **GR-2.2** Borrowed terms are credited to their originator; terms introduced by this site
  are marked *coined*. *(check: glossary attribution)*
- **GR-2.3** No invented statistics, case studies, quotes or anecdotes. Where no public
  evidence exists, the page presents the practice as recommended practice, not as a finding.
  *(review: accuracy)*
- **GR-2.4** A cited source must say what the page claims it says. *(review: accuracy)*
- **GR-2.5** Every reference records title, author or organisation, URL and date accessed.
  Links are checked on every build. *(check)*

## §3 Voice

- **GR-3.1** Reference-material register: present tense, authoritative, plain practitioner
  English. No first person. No statements about any organisation's progress. *(review: style)*
- **GR-3.2** No provisional language anywhere on the site: "draft", "work in progress",
  "coming soon", "TBD", "to be added", "placeholder", "v0.x". Map boxes without a page are shown
  as plain labels, never as "coming". *(check: banned phrases)*
- **GR-3.3** Vendor-neutral by default. A product is named only on a page about its category,
  and only as one example among several. *(check: product-name list · review: style)*
- **GR-3.4** The running example (customer-record export) is the only worked example unless the
  author approves another. *(review: style)*

## §4 Completeness

- **GR-4.1** A page is published only when complete: every required section of its page-type
  template is present and substantive. *(check: template structure · review: editorial)*
- **GR-4.2** Every page stands alone. A reader arriving from search understands it without
  reading another page first. *(review: editorial)*
- **GR-4.3** Every internal link resolves to a published page or anchor. *(check)*
- **GR-4.4** Every diagram is diagram-as-code, has a text alternative, and renders in light and
  dark themes. *(check)*

## §5 Process

- **GR-5.1 Repeatable.** Every page goes through the same pipeline (see `APPROACH.md`), run by
  named agents whose prompts and templates are versioned in the repository.
- **GR-5.2 Verifiable.** Every published page has a review record in `reviews/` listing the
  sources used, each reviewer's verdict with findings, and the human approver. CI refuses to
  publish a page without an ACCEPT from every required reviewer. *(check)*
- **GR-5.3 Improvable.** Reviewer findings are logged by rule number. After each wave a
  retrospective decides whether a rule, template, prompt or check changes. A finding that
  recurs becomes an automated check where possible. Changes are recorded in `DECISIONS.md` and
  the changelog.
- **GR-5.4** `main` always builds and passes validation. Work lands through pull requests.

## §6 Authority

- **GR-6.1** The author approves these rules, each wave plan, and the first publication of
  every page in wave 1. Later waves may use agent-only approval for small edits if the author
  agrees in `DECISIONS.md`.
- **GR-6.2** Where a rule conflicts with a request in a session, the rule wins until the author
  changes it here.
