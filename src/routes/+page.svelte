<script lang="ts">
  import { description, profile } from '$lib/profile';

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: profile.name,
    jobTitle: profile.title,
    email: profile.email,
    telephone: profile.phone,
    sameAs: [profile.github]
  };
  const structuredDataJson = JSON.stringify(structuredData).replace(/</g, '\\u003c');
</script>

<svelte:head>
  <title>{profile.name} — {profile.title}</title>
  <meta name="description" content={description} />
  <meta name="author" content={profile.name} />
  <meta name="robots" content="index, follow" />
  <meta name="color-scheme" content="dark" />
  <meta name="theme-color" content="#090d12" />
  <meta property="og:type" content="profile" />
  <meta property="og:site_name" content={profile.name} />
  <meta property="og:title" content={`${profile.name} — ${profile.title}`} />
  <meta property="og:description" content={description} />
  <meta property="og:locale" content="en_US" />
  <meta property="profile:first_name" content={profile.firstName} />
  <meta property="profile:last_name" content={profile.lastName} />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content={`${profile.name} — ${profile.title}`} />
  <meta name="twitter:description" content={description} />
  {@html `<script type="application/ld+json">${structuredDataJson}</script>`}
</svelte:head>

<main class="profile">
  <div class="profile-mark" aria-hidden="true">
    <span>M</span>
    <span>S</span>
    <span>N</span>
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
      <span>{profile.firstName}</span>
      <span class="name-last">{profile.lastName}<span class="name-period">.</span></span>
    </h1>
    <p class="role">{profile.title}</p>
    <nav class="contact" aria-label="Contact information">
      <a class="contact-link" href={`mailto:${profile.email}`}>
        <span class="contact-label">Email</span>
        <span class="contact-value">{profile.email}</span>
        <span class="contact-arrow" aria-hidden="true">↗</span>
      </a>
      <a class="contact-link" href={`tel:${profile.phoneLink}`}>
        <span class="contact-label">Phone</span>
        <span class="contact-value">{profile.phone}</span>
        <span class="contact-arrow" aria-hidden="true">↗</span>
      </a>
      <a class="contact-link" href={profile.github} rel="noreferrer">
        <span class="contact-label">GitHub</span>
        <span class="contact-value">{profile.githubLabel}</span>
        <span class="contact-arrow" aria-hidden="true">↗</span>
      </a>
    </nav>
  </section>
</main>
