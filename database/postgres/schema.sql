CREATE TABLE intel_sources (



    id SERIAL PRIMARY KEY,



    name VARCHAR(100) NOT NULL,



    source_type VARCHAR(50),



    api_endpoint TEXT,



    trust_score INTEGER DEFAULT 50,



    last_sync TIMESTAMP,



    status VARCHAR(20) DEFAULT 'active',



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
CREATE TABLE indicators (



    id SERIAL PRIMARY KEY,



    indicator_type VARCHAR(50) NOT NULL,



    indicator_value TEXT NOT NULL,



    source_id INTEGER REFERENCES intel_sources(id),



    confidence INTEGER,



    severity VARCHAR(20),



    tlp VARCHAR(20),



    first_seen TIMESTAMP,



    last_seen TIMESTAMP,



    status VARCHAR(20) DEFAULT 'active',



    tags TEXT[],



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
CREATE TABLE vulnerabilities (



    id SERIAL PRIMARY KEY,



    cve_id VARCHAR(30) UNIQUE,



    title TEXT,



    description TEXT,



    vendor VARCHAR(100),



    product VARCHAR(100),



    cvss_score DECIMAL(3,1),



    severity VARCHAR(20),



    attack_vector VARCHAR(50),



    attack_complexity VARCHAR(50),



    privileges_required VARCHAR(50),



    user_interaction VARCHAR(50),



    cwe VARCHAR(50),



    exploit_available BOOLEAN DEFAULT FALSE,



    published_date DATE,



    modified_date DATE,



    source_id INTEGER REFERENCES intel_sources(id),



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
CREATE TABLE exploited_vulnerabilities (



    id SERIAL PRIMARY KEY,



    cve_id VARCHAR(30),



    vendor VARCHAR(100),



    product VARCHAR(100),



    date_added DATE,



    ransomware_use BOOLEAN DEFAULT FALSE,



    notes TEXT



);
CREATE TABLE malware_families (



    id SERIAL PRIMARY KEY,



    name VARCHAR(100),



    category VARCHAR(100),



    platform VARCHAR(50),



    description TEXT,



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
CREATE TABLE malware_samples (



    id SERIAL PRIMARY KEY,



    sha256 VARCHAR(100),



    sha1 VARCHAR(100),



    md5 VARCHAR(50),



    file_name TEXT,



    file_type VARCHAR(50),



    malware_family_id INTEGER REFERENCES malware_families(id),



    first_seen TIMESTAMP,



    source_id INTEGER REFERENCES intel_sources(id)



);
CREATE TABLE threat_actors (



    id SERIAL PRIMARY KEY,



    name VARCHAR(100),



    aliases TEXT[],



    motivation VARCHAR(100),



    description TEXT,



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP



);
CREATE TABLE campaigns (



    id SERIAL PRIMARY KEY,



    name VARCHAR(150),



    description TEXT,



    threat_actor_id INTEGER REFERENCES threat_actors(id),



    target_sector VARCHAR(100),



    start_date DATE,



    end_date DATE



);
CREATE TABLE attack_techniques (



    id SERIAL PRIMARY KEY,



    technique_id VARCHAR(20),



    name VARCHAR(150),



    tactic VARCHAR(100),



    description TEXT



);
CREATE TABLE cyber_news (



    id SERIAL PRIMARY KEY,



    title TEXT,



    summary TEXT,



    url TEXT,



    source VARCHAR(100),



    category VARCHAR(100),



    severity VARCHAR(20),



    published_date TIMESTAMP,



    tags TEXT[]



);
CREATE TABLE security_advisories (



    id SERIAL PRIMARY KEY,



    vendor VARCHAR(100),



    advisory_id VARCHAR(100),



    title TEXT,



    description TEXT,



    related_cves TEXT[],



    severity VARCHAR(20),



    published_date DATE



);
CREATE TABLE threat_reports (



    id SERIAL PRIMARY KEY,



    title TEXT,



    organization VARCHAR(100),



    report_type VARCHAR(50),



    summary TEXT,



    url TEXT,



    published_date DATE



);
CREATE TABLE breach_events (



    id SERIAL PRIMARY KEY,



    organization VARCHAR(150),



    industry VARCHAR(100),



    attack_type VARCHAR(100),



    threat_actor VARCHAR(100),



    impact TEXT,



    incident_date DATE,



    source TEXT



);
CREATE TABLE feed_history (



    id SERIAL PRIMARY KEY,



    source_id INTEGER REFERENCES intel_sources(id),



    records_received INTEGER,



    records_processed INTEGER,



    status VARCHAR(20),



    error_message TEXT,



    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP



);

