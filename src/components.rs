//! Leptos components that describe the portfolio markup.

use leptos::prelude::*;

use crate::data;
use crate::styles;

#[component]
pub fn Masthead() -> impl IntoView {
    view! {
        <header class="masthead">
            <p class="eyebrow">"Systems Engineer"</p>
            <h1>{data::NAME}</h1>
            <p class="role">{data::TITLE}</p>
            <div class="contact">
                <a href=format!("mailto:{}", data::EMAIL)>{data::EMAIL}</a>
                <span>{data::PHONE}</span>
                <a href=data::GITHUB rel="noreferrer">
                    {data::GITHUB_LABEL}
                </a>
            </div>
            <div class="thesis">
                <p>{data::THESIS}</p>
            </div>
        </header>
    }
}

#[component]
pub fn About() -> impl IntoView {
    view! {
        <section id="about">
            <h2>"About"</h2>
            <p class="lede">{data::SUMMARY}</p>
        </section>
    }
}

#[component]
pub fn ExperienceSection() -> impl IntoView {
    view! {
        <section id="experience">
            <h2>"Experience"</h2>
            <div class="timeline">
                {data::EXPERIENCE
                    .iter()
                    .map(|job| {
                        view! {
                            <article class="entry">
                                <h3>{job.role}</h3>
                                <div class="meta">
                                    <span class="org">{job.org}</span>
                                    <span>{job.location}</span>
                                    <span>{job.period}</span>
                                </div>
                                <ul class="ticks">
                                    {job
                                        .highlights
                                        .iter()
                                        .map(|point| view! { <li>{*point}</li> })
                                        .collect_view()}
                                </ul>
                            </article>
                        }
                    })
                    .collect_view()}
            </div>
        </section>
    }
}

#[component]
pub fn EducationSection() -> impl IntoView {
    view! {
        <section id="education">
            <h2>"Education"</h2>
            <div class="timeline">
                {data::EDUCATION
                    .iter()
                    .map(|entry| {
                        view! {
                            <article class="entry">
                                <h3>{entry.degree}</h3>
                                <div class="meta">
                                    <span class="org">{entry.school}</span>
                                    <span>{entry.location}</span>
                                    <span>{entry.period}</span>
                                </div>
                                <ul class="ticks">
                                    {entry
                                        .notes
                                        .iter()
                                        .map(|note| view! { <li>{*note}</li> })
                                        .collect_view()}
                                </ul>
                            </article>
                        }
                    })
                    .collect_view()}
            </div>
        </section>
    }
}

#[component]
pub fn Skills() -> impl IntoView {
    view! {
        <section id="skills">
            <h2>"Skills"</h2>
            <div class="grid">
                {data::SKILLS
                    .iter()
                    .map(|group| {
                        view! {
                            <div class="card">
                                <span class="label">{group.label}</span>
                                <div class="tags">
                                    {group
                                        .items
                                        .iter()
                                        .map(|item| view! { <span class="tag">{*item}</span> })
                                        .collect_view()}
                                </div>
                            </div>
                        }
                    })
                    .collect_view()}
            </div>
        </section>
    }
}

#[component]
pub fn Certifications() -> impl IntoView {
    view! {
        <section id="certifications">
            <h2>"Certifications"</h2>
            <div class="card cert">
                {data::CERTIFICATIONS
                    .iter()
                    .map(|cert| {
                        view! {
                            <div class="row">
                                <span class="who">{cert.name}</span>
                                <span class="id">
                                    {format!("{} \u{00b7} {}", cert.issuer, cert.credential)}
                                </span>
                            </div>
                        }
                    })
                    .collect_view()}
            </div>
        </section>
    }
}

#[component]
pub fn Languages() -> impl IntoView {
    view! {
        <section id="languages">
            <h2>"Languages"</h2>
            <div class="tags">
                {data::LANGUAGES
                    .iter()
                    .map(|lang| {
                        view! {
                            <span class="tag accent">
                                {format!("{} \u{00b7} {}", lang.name, lang.level)}
                            </span>
                        }
                    })
                    .collect_view()}
            </div>
        </section>
    }
}

#[component]
pub fn Activity() -> impl IntoView {
    view! {
        <section id="activity">
            <h2>"Coding Activity"</h2>
            <p class="lede">
                "Live WakaTime telemetry, rendered to static SVG by the same Rust pipeline \
                 that builds this page."
            </p>
            <div class="charts">
                {data::CHARTS
                    .iter()
                    .map(|chart| {
                        view! {
                            <div class="chart">
                                <h4>{chart.title}</h4>
                                <div inner_html=chart.svg></div>
                            </div>
                        }
                    })
                    .collect_view()}
            </div>
        </section>
    }
}

#[component]
pub fn Footer() -> impl IntoView {
    view! {
        <footer>
            <span>{data::MOTTO}</span>
            <span>{format!("\u{00a9} {} \u{00b7} Built with Rust + Leptos", data::NAME)}</span>
        </footer>
    }
}

/// The complete page. Shared by the static generator and any future renderer.
#[component]
pub fn App() -> impl IntoView {
    view! {
        <div class="page">
            <Masthead/>
            <About/>
            <ExperienceSection/>
            <EducationSection/>
            <Skills/>
            <Certifications/>
            <Languages/>
            <Activity/>
            <Footer/>
        </div>
    }
}

/// Emits the document shell and the Rust-authored stylesheet.
pub fn document() -> String {
    shell(crate::render(App))
}

/// Standalone page served by the host for unmatched routes.
#[component]
pub fn NotFound() -> impl IntoView {
    view! {
        <div class="page">
            <header class="masthead">
                <p class="eyebrow">"404"</p>
                <h1>"Page not found"</h1>
                <p class="role">"That route does not exist on this site."</p>
            </header>
            <section>
                <a href="/">"\u{2190} Return to the portfolio"</a>
            </section>
        </div>
    }
}

pub fn not_found_document() -> String {
    shell(crate::render(NotFound))
}

/// Wraps rendered body markup in the shared document shell.
fn shell(body: String) -> String {
    format!(
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n\
<meta charset=\"utf-8\">\n\
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n\
<title>{name} \u{2014} {title}</title>\n\
<meta name=\"description\" content=\"{description}\">\n\
<meta property=\"og:title\" content=\"{name} \u{2014} {title}\">\n\
<meta property=\"og:description\" content=\"{description}\">\n\
<meta property=\"og:type\" content=\"profile\">\n\
<meta name=\"color-scheme\" content=\"dark\">\n\
<meta name=\"theme-color\" content=\"{theme}\">\n\
<style>\n{style}\n</style>\n\
</head>\n<body>\n{body}\n</body>\n</html>\n",
        name = data::NAME,
        title = data::TITLE,
        description = data::SUMMARY,
        theme = styles::THEME_COLOR,
        style = styles::stylesheet(),
        body = body,
    )
}
