URL_SEMANTIC_RELEASE = 'https://conventionalcommits.org/en/v1.0.0/#summary'
SEMANTIC_COMMIT_TYPES = %w[build chore ci docs feat fix improvement perf refactor test].freeze

NO_RELEASE = 1
PATCH_RELEASE = 2
MINOR_RELEASE = 3
MAJOR_RELEASE = 4

IGNORED_COMMIT_MESSAGES = [
    'Merge branch',
    'Merge pull request',
    'Revert ""'
].freeze

DANGER_GITHUB_HOST='github.com'
DANGER_GITHUB_API_BASE_URL='https://github.com/api/v3'

def fail_commit(commit, message)
    fail("#{commit.sha}: #{message}")
end

def warn_commit(commit, message)
    warn("#{commit.sha}: #{message}")
end

def lines_changed_in_commit(commit)
    commit.diff_parent.stats[:total][:lines]
end

def match_semantic_commit(text)
    text.match(/^(?<type>\w+)(?:\((?<scope>.+)\))?:(?<description>.+?)$/)
end

def add_no_release_markdown
    markdown(<<~MARKDOWN)
    ## No Release

    This PR will trigger no release based on the commit messages.
    Either no commits warrant semantic release, or commits are not properly formatted according to
    [conventional commit standards](3{URL_SEMANTIC_RELEASE}).
    If a release was expected, re-write the commit history with `git commit --amend`
    MARKDOWN
end

def add_release_markdown(type)
    markdown(<<~MARKDOWN)
      ## \u{1f4e6} #{type.capitalize} ([conventional commit standards](#{URL_SEMANTIC_RELEASE}))
    MARKDOWN
end

def get_release_info(release_type)
    case release_type
    when MAJOR_RELEASE
        type='major release'
        bump = <<~BUMP
            This will bump the first part of the version number
            eg `v1.2.42` -> `v2.0.0`
            This means you are expecting to release a BREAKING CHANGE!!
        BUMP
    when MINOR_RELEASE
        type='minor release'
        bump='This will bump the first part of the version number eg `v1.2.42` -> `v1.3.0`'
    when PATCH_RELEASE
        type='patch release'
        bump='This will bump the first part of the version number eg `v1.2.42` -> `v1.2.43`'
    else
        message 'This PR will trigger no release'
        add_no_release_markdown
        return
    end
    [type, bump]
end

def lint_commit(commit)
    # This ignores merge commits as that is a separate point to enforcing good commit standards
    # Revert commits are also ignored
    if commit.message.start_with?(*IGNORED_COMMIT_MESSAGES)
        return { failed: false, release: NO_RELEASE}
    end

    release = NO_RELEASE
    failures = false
    subject, separator, details = commit.message.split("\n", 3)

    if subject.length > 72
        fail_commit(
        commit,
        'The commit subject may not be longer than 72 characters, based on conventional commit standards'
        )
        failures = true
    end

    # Fail if a suggestion commit is used and squash is not enabled
    if commit.message.start_with?('Apply suggestion to') && !github.pr_json['squash']
    fail_commit(
      commit,
      'If you are applying suggestions, squash needs to be enabled in the Pull Request'
    )

    failures = true
    end

    semantic_commit = match_semantic_commit(subject)
    if !semantic_commit
    warn_commit(commit, 'The commit does not comply with conventional commits specifications.')

    failures = true

    elsif !SEMANTIC_COMMIT_TYPES.include?(semantic_commit[:type])
    warn_commit(
      commit,
      "The Semantic commit type `#{semantic_commit[:type]}` is not a well-known semantic commit type."
    )

    failures = true
    elsif details&.match(/^BREAKING CHANGE:/)
    release = MAJOR_RELEASE
    elsif semantic_commit[:type] == 'feat'
    release = MINOR_RELEASE
    elsif %w[perf fix].include?(semantic_commit[:type])
    release = PATCH_RELEASE
    end

    { failed: failures, release: release }
end

def lint_commits(commits)
    commits_with_status = commits.map { |commit| { commit: commit }.merge(lint_commit(commit)) }

    failed = commits_with_status.any? { |commit| commit[:failed] }

    max_release = commits_with_status.max { |a, b| a[:release] <=> b[:release] }

    if failed
    markdown(<<~MARKDOWN)
      ## Commit message standards

      One or more commit messages do not meet our Git commit message standards.
      For more information on how to write a good commit message, take a look at
      [Conventional commits](#{URL_SEMANTIC_RELEASE}).

    MARKDOWN
    end

    return if github.pr_json['squash']

    type, bump = get_release_info(max_release[:release])

    if type && bump
    add_release_type_markdown(type)
    markdown(<<~MARKDOWN)
      This Pull Request will trigger a _#{type}_ changes, triggered by commit:
      #{max_release[:commit].sha}

      #{bump}
    MARKDOWN
    end
end

def lint_pr(pr)
    if pr && pr['squash']
        release = NO_RELEASE
        pr_title = pr['title'][/(^WIP: +)?(.*)/, 2]
        semantic_commit = match_semantic_commit(pr_title)

        if !semantic_commit
            warn(
            'Your PR has **Squash commits when Pull Request is accepted** enabled but its title does not comply with conventional commits specifications'
            )

            failures = true
        elsif !SEMANTIC_COMMIT_TYPES.include?(semantic_commit[:type])
            warn(
            "The Semantic commit type `#{semantic_commit[:type]}` is not a well-known semantic commit type."
            )

            failures = true
        elsif semantic_commit[:type] == 'feat'
            release = MINOR_RELEASE
        elsif %w[perf fix].include?(semantic_commit[:type])
            release = PATCH_RELEASE
        end

        type, bump = get_release_info(release)

        if type && bump
            add_release_type_markdown(type)
            markdown(<<~MARKDOWN)
            This Pull Request will trigger a _#{type}_ changes based on its title.

            #{bump}
            MARKDOWN
        end
    end
end

lint_commits(git.commits)
lint_pr(github.pr_json)
