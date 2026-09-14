//! Static content for the portfolio, transcribed from `resume.tex` and the
//! WakaTime statistics stored elsewhere in the repository.

pub struct Experience {
    pub role: &'static str,
    pub org: &'static str,
    pub location: &'static str,
    pub period: &'static str,
    pub highlights: &'static [&'static str],
}

pub const NAME: &str = "Mahadi Sajjad Neloy";
pub const TITLE: &str = "Systems Engineer";
pub const EMAIL: &str = "mahadi.s.neloy@gmail.com";
pub const PHONE: &str = "+880 1945 521324";
pub const GITHUB: &str = "https://github.com/msneloy";
pub const GITHUB_LABEL: &str = "github.com/msneloy";

pub const SUMMARY: &str = "Systems Engineer specialising in embedded systems, IoT architecture, \
and network infrastructure, with a track record of building operational technical environments \
from nothing and a simple policy \u{2014} problems get solved, or I find somewhere that lets me \
solve them.";

pub const MOTTO: &str = "Problems get solved, or I find somewhere that lets me solve them.";

/// The two-versions line from the top of the repository README, kept verbatim.
pub const THESIS: &str = "There are two versions of my work. One is documented, tested, and \
built to last. The other is functional. Which one you receive depends entirely on you.";

pub const EXPERIENCE: &[Experience] = &[
    Experience {
        role: "Head of Engineering",
        org: "Mentors' Noakhali Branch",
        location: "Noakhali, Bangladesh",
        period: "Jun 2025 \u{2014} Aug 2026",
        highlights: &[
            "Architected complete technical infrastructure for a two-floor facility from bare \
construction \u{2014} three-phase electrical load distribution, structured Cat6 cabling with \
RJ45 ports in every room, custom network rack fabrication, UPS power segmentation across \
critical and non-critical systems, and dual-band access point placement.",
            "Specified, procured, and deployed 30+ purpose-built Linux workstations across all \
departments, including a high-performance multimedia production station, eliminating Windows \
attack surface across the fleet.",
            "Designed and hardened a multi-floor enterprise network via internal penetration \
assessment encompassing DDoS simulation and unauthorised access vector testing, resulting in \
full port closure and firewall hardening on branch routing infrastructure.",
            "Diagnosed and resolved a Path MTU blackhole caused by PPPoE frame limitation \
silently dropping TLS handshake packets \u{2014} independently, without ISP support following \
provider acquisition and engineering staff replacement.",
            "Developed BIFROST, a proprietary screen broadcasting platform supporting \
multi-client connectivity, real-time audio transmission, and live connection monitoring \
\u{2014} sole engineer from concept to deployment.",
            "Designed and deployed Cerberus, a full-stack IELTS preparation platform with \
AI-assisted evaluation, real-time answer saving, and mock test infrastructure, developed \
iteratively against a structured feature request pipeline.",
            "Built and maintained the branch website including data-driven architecture \
migration, SEO implementation across 1,000 keywords, and dynamic content systems.",
            "Deployed iPBX call centre infrastructure with 10 extensions, call recording, and \
bulk SMS capability registered across all four national telecommunications providers via BTCL.",
            "Established branch-wide cloud data infrastructure, access control, and \
documentation standards \u{2014} migrating all operations from ad hoc file sharing to a \
structured, centralised repository.",
            "Trained and mentored two junior technical staff in hardware assembly, Linux \
administration, networking fundamentals, and electrical systems.",
        ],
    },
    Experience {
        role: "Embedded Systems Engineer",
        org: "Youth Notion",
        location: "Noakhali, Bangladesh",
        period: "Aug 2023 \u{2014} May 2025",
        highlights: &[
            "Lead Hardware & Software Engineer on TERRA \u{2014} real-time flood monitoring \
network featuring ESP8266 nodes, multi-sensor array (ultrasonic, DHT22, MQ135), tri-mode \
connectivity (WiFi/GSM/LoRaWAN), solar and battery power management, and a centralised \
geographic dashboard \u{2014} prototype competition-validated and reviewed by Bangladesh ICT \
Ministry.",
            "Embedded Systems Engineer on BLADE \u{2014} IoT aquaculture management system \
featuring ESP32-based embedded hardware, REST API cloud infrastructure, real-time multi-sensor \
biofloc telemetry, and automated electromechanical control \u{2014} validated against \
traditional recirculating systems with a 10% improvement in survival rate and 3.2% improvement \
in growth rate.",
            "Embedded Systems Engineer on ARROW \u{2014} smart pen system for Bengali handwriting \
education featuring STM32F4 firmware, 6-axis IMU stroke capture with Kalman filtering, BLE 5.0 \
data transmission, and TensorFlow Lite neural network inference \u{2014} feasibility validated \
against Bengali script requirements with manufacturing pipeline established.",
        ],
    },
    Experience {
        role: "Systems Engineer",
        org: "Kuayue (Huzhou) Technology Co., Ltd.",
        location: "Zhengzhou, Henan, China",
        period: "Dec 2022 \u{2014} Jul 2023",
        highlights: &[
            "Recruited directly by CEO from university research laboratory to lead embedded \
systems prototyping for client-driven automation and AI projects \u{2014} developed hardware \
and firmware prototypes through viability validation for handoff to mass production pipeline.",
            "Principal engineer on autonomous vehicle and UAV development projects, working \
across embedded firmware, sensor integration, and system architecture.",
        ],
    },
    Experience {
        role: "Applications Engineer",
        org: "Kuayue (Huzhou) Technology Co., Ltd.",
        location: "Huzhou, Zhejiang, China",
        period: "Jul 2021 \u{2014} Dec 2022",
        highlights: &[
            "Developed embedded application prototypes against client specifications, \
collaborating with senior engineers on system architecture and viability assessment prior to \
production handoff.",
        ],
    },
    Experience {
        role: "Research Analyst",
        org: "Cyberspace Security Laboratory \u{2014} HUTC",
        location: "Huzhou, Zhejiang, China",
        period: "Jan 2020 \u{2014} Jul 2021",
        highlights: &[
            "Conducted applied research in network security and embedded systems, contributing \
to laboratory publications and prototype development.",
        ],
    },
    Experience {
        role: "Research Assistant",
        org: "IoT Competition Laboratory \u{2014} HUTC",
        location: "Huzhou, Zhejiang, China",
        period: "Sep 2017 \u{2014} Dec 2019",
        highlights: &[
            "Designed and built IoT prototypes for national and university level competitions, \
placing 1st in the 3rd Huzhou University IoT Application Innovation Competition (2018).",
        ],
    },
];

pub struct Education {
    pub degree: &'static str,
    pub school: &'static str,
    pub location: &'static str,
    pub period: &'static str,
    pub notes: &'static [&'static str],
}

pub const EDUCATION: &[Education] = &[Education {
    degree: "Bachelor of Engineering \u{2014} Computer Science",
    school: "School of Information Engineering, Huzhou University",
    location: "Huzhou, Zhejiang, China",
    period: "Sep 2017 \u{2014} Jul 2021",
    notes: &[
        "Thesis: Industrial Automation with ESP8266",
        "Zhejiang Provincial Government Scholarship (Class B), 2021",
        "National College Student Innovation and Entrepreneurship Training Project Winner, 2019",
        "1st Prize, 5th Huzhou University IoT Application Innovation Competition, 2020",
        "1st Prize, 3rd Huzhou University IoT Application Innovation Competition, 2018",
        "University Scholarship for International Students (Type A), 2017",
    ],
}];

pub struct SkillGroup {
    pub label: &'static str,
    pub items: &'static [&'static str],
}

pub const SKILLS: &[SkillGroup] = &[
    SkillGroup { label: "Languages", items: &["C", "C++", "Python", "Java", "Bash", "Rust"] },
    SkillGroup { label: "Embedded", items: &["ESP32", "ESP8266", "STM32", "Arduino", "ARM"] },
    SkillGroup { label: "Systems", items: &["Linux", "Git", "MQTT", "REST", "TLS", "LoRaWAN"] },
    SkillGroup {
        label: "Networking",
        items: &["Architecture", "Penetration Testing", "VoIP", "Firewall"],
    },
    SkillGroup { label: "Platforms", items: &["TensorFlow Lite", "OpenCV", "Firebase", "Kafka"] },
];

pub struct Certification {
    pub name: &'static str,
    pub issuer: &'static str,
    pub credential: &'static str,
}

pub const CERTIFICATIONS: &[Certification] = &[
    Certification {
        name: "CNSS Certified Network Security Specialist",
        issuer: "ICSI, UK",
        credential: "20379392",
    },
    Certification {
        name: "OSS Development, Linux and Git Specialization",
        issuer: "Linux Foundation",
        credential: "DXLZHCPYVALL",
    },
    Certification {
        name: "Google IT Automation Professional Certificate",
        issuer: "Google",
        credential: "V2VN7MZRSB79",
    },
];

pub struct SpokenLanguage {
    pub name: &'static str,
    pub level: &'static str,
}

pub const LANGUAGES: &[SpokenLanguage] = &[
    SpokenLanguage { name: "Bengali", level: "Native" },
    SpokenLanguage { name: "Mandarin Chinese", level: "HSK 2" },
    SpokenLanguage { name: "English", level: "IELTS Band 8" },
];

/// Static WakaTime charts, embedded verbatim from `.github/wakatime`.
pub struct Chart {
    pub title: &'static str,
    pub svg: &'static str,
}

pub const CHARTS: &[Chart] = &[
    Chart { title: "Summary", svg: include_str!("../.github/wakatime/summary.svg") },
    Chart { title: "Languages", svg: include_str!("../.github/wakatime/languages.svg") },
    Chart { title: "Editors", svg: include_str!("../.github/wakatime/editors.svg") },
    Chart {
        title: "Operating Systems",
        svg: include_str!("../.github/wakatime/operating-systems.svg"),
    },
    Chart { title: "Categories", svg: include_str!("../.github/wakatime/categories.svg") },
];
