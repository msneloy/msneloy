//! Leptos components that describe the single-page profile.

use leptos::prelude::*;

use crate::data;
use crate::styles;

#[component]
pub fn Profile() -> impl IntoView {
    view! {
        <main class="profile">
            <div class="profile-mark" aria-hidden="true">
                <span>"M"</span>
                <span>"S"</span>
                <span>"N"</span>
            </div>
            <div class="orbit" aria-hidden="true">
                <span class="orbit-core"></span>
                <span class="orbit-ring orbit-ring-one"></span>
                <span class="orbit-ring orbit-ring-two"></span>
                <span class="orbit-line"></span>
                <span class="orbit-node orbit-node-one"></span>
                <span class="orbit-node orbit-node-two"></span>
                <span class="orbit-node orbit-node-three"></span>
            </div>
            <section class="intro" aria-labelledby="name">
                <h1 id="name">
                    <span>{data::NAME_LINE_ONE}</span>
                    <span class="name-last">{data::NAME_LINE_TWO}<span class="name-period">.</span></span>
                </h1>
                <p class="role">{data::TITLE}</p>
                <nav class="contact" aria-label="Contact information">
                    <a class="contact-link" href=format!("mailto:{}", data::EMAIL)>
                        <span class="contact-label">"Email"</span>
                        <span class="contact-value">{data::EMAIL}</span>
                        <span class="contact-arrow" aria-hidden="true">"↗"</span>
                    </a>
                    <a class="contact-link" href=format!("tel:{}", data::PHONE_LINK)>
                        <span class="contact-label">"Phone"</span>
                        <span class="contact-value">{data::PHONE}</span>
                        <span class="contact-arrow" aria-hidden="true">"↗"</span>
                    </a>
                    <a class="contact-link" href=data::GITHUB rel="noreferrer">
                        <span class="contact-label">"GitHub"</span>
                        <span class="contact-value">{data::GITHUB_LABEL}</span>
                        <span class="contact-arrow" aria-hidden="true">"↗"</span>
                    </a>
                </nav>
            </section>
        </main>
    }
}

/// Emits the complete single-page document and Rust-authored stylesheet.
pub fn document() -> String {
    shell(crate::render(Profile))
}

fn shell(body: String) -> String {
    format!(
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n\
<meta charset=\"utf-8\">\n\
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n\
<meta name=\"color-scheme\" content=\"dark\">\n\
<meta name=\"theme-color\" content=\"{theme}\">\n\
<meta name=\"description\" content=\"{description}\">\n\
<meta property=\"og:type\" content=\"profile\">\n\
<meta property=\"og:title\" content=\"{name} \u{2014} {title}\">\n\
<meta property=\"og:description\" content=\"{description}\">\n\
<title>{name} \u{2014} {title}</title>\n\
<style>\n{style}\n</style>\n\
</head>\n<body>\n{body}\n</body>\n</html>\n",
        theme = styles::THEME_COLOR,
        description = format!("{} \u{2014} {}", data::NAME, data::TITLE),
        name = data::NAME,
        title = data::TITLE,
        style = styles::stylesheet(),
        body = body,
    )
}

#[cfg(test)]
mod tests {
    use super::document;
    use crate::data;

    #[test]
    fn renders_one_profile_with_all_contact_methods() {
        let html = document();

        assert_eq!(html.matches("<main").count(), 1);
        assert_eq!(html.matches("<h1").count(), 1);
        assert!(html.contains(data::NAME));
        assert!(html.contains(data::TITLE));
        assert!(html.contains(data::EMAIL));
        assert!(html.contains(&format!("mailto:{}", data::EMAIL)));
        assert!(html.contains(data::PHONE));
        assert!(html.contains(&format!("tel:{}", data::PHONE_LINK)));
        assert!(html.contains(data::GITHUB));
        assert!(html.contains(data::GITHUB_LABEL));
        assert!(!html.contains("Experience"));
        assert!(!html.contains("<script"));
    }
}
