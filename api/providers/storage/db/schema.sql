--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: espa; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA espa;


ALTER SCHEMA espa OWNER TO postgres;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = espa, pg_catalog;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.auth_group_id_seq OWNER TO espa;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE auth_group (
    id integer DEFAULT nextval('auth_group_id_seq'::regclass) NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE espa.auth_group OWNER TO espa;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.auth_group_permissions_id_seq OWNER TO espa;

--
-- Name: auth_group_permissions; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer DEFAULT nextval('auth_group_permissions_id_seq'::regclass) NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE espa.auth_group_permissions OWNER TO espa;

--
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.auth_message_id_seq OWNER TO espa;

--
-- Name: auth_message; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE auth_message (
    id integer DEFAULT nextval('auth_message_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE espa.auth_message OWNER TO espa;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.auth_permission_id_seq OWNER TO espa;

--
-- Name: auth_permission; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer DEFAULT nextval('auth_permission_id_seq'::regclass) NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE espa.auth_permission OWNER TO espa;

--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.auth_user_id_seq OWNER TO espa;

--
-- Name: auth_user; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE auth_user (
    id integer DEFAULT nextval('auth_user_id_seq'::regclass) NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp without time zone NOT NULL,
    date_joined timestamp without time zone NOT NULL
);


ALTER TABLE espa.auth_user OWNER TO espa;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.auth_user_groups_id_seq OWNER TO espa;

--
-- Name: auth_user_groups; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer DEFAULT nextval('auth_user_groups_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE espa.auth_user_groups OWNER TO espa;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.auth_user_user_permissions_id_seq OWNER TO espa;

--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE espa.auth_user_user_permissions OWNER TO espa;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.django_admin_log_id_seq OWNER TO espa;

--
-- Name: django_admin_log; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer DEFAULT nextval('django_admin_log_id_seq'::regclass) NOT NULL,
    action_time timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag integer NOT NULL,
    change_message text NOT NULL
);


ALTER TABLE espa.django_admin_log OWNER TO espa;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.django_content_type_id_seq OWNER TO espa;

--
-- Name: django_content_type; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer DEFAULT nextval('django_content_type_id_seq'::regclass) NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE espa.django_content_type OWNER TO espa;

--
-- Name: django_migrations; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE espa.django_migrations OWNER TO espa;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.django_migrations_id_seq OWNER TO espa;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: espa; Owner: espa
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp without time zone NOT NULL
);


ALTER TABLE espa.django_session OWNER TO espa;

--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.django_site_id_seq OWNER TO espa;

--
-- Name: django_site; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE django_site (
    id integer DEFAULT nextval('django_site_id_seq'::regclass) NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE espa.django_site OWNER TO espa;

--
-- Name: ordering_configuration_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_configuration_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_configuration_id_seq OWNER TO espa;

--
-- Name: ordering_configuration; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_configuration (
    id integer DEFAULT nextval('ordering_configuration_id_seq'::regclass) NOT NULL,
    key character varying(255) NOT NULL,
    value character varying(2048) NOT NULL
);


ALTER TABLE espa.ordering_configuration OWNER TO espa;

--
-- Name: ordering_datapoint_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_datapoint_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_datapoint_id_seq OWNER TO espa;

--
-- Name: ordering_datapoint; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_datapoint (
    id integer DEFAULT nextval('ordering_datapoint_id_seq'::regclass) NOT NULL,
    key character varying(250) NOT NULL,
    command character varying(2048) NOT NULL,
    description text,
    enable boolean NOT NULL,
    last_updated timestamp without time zone
);


ALTER TABLE espa.ordering_datapoint OWNER TO espa;

--
-- Name: ordering_datapoint_tags_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_datapoint_tags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_datapoint_tags_id_seq OWNER TO espa;

--
-- Name: ordering_datapoint_tags; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_datapoint_tags (
    id integer DEFAULT nextval('ordering_datapoint_tags_id_seq'::regclass) NOT NULL,
    datapoint_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE espa.ordering_datapoint_tags OWNER TO espa;

--
-- Name: ordering_datasource_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_datasource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_datasource_id_seq OWNER TO espa;

--
-- Name: ordering_datasource; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_datasource (
    id integer DEFAULT nextval('ordering_datasource_id_seq'::regclass) NOT NULL,
    name character varying(255) NOT NULL,
    username character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    host character varying(255) NOT NULL,
    port integer NOT NULL
);


ALTER TABLE espa.ordering_datasource OWNER TO espa;

--
-- Name: ordering_download_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_download_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_download_id_seq OWNER TO espa;

--
-- Name: ordering_download; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_download (
    id integer DEFAULT nextval('ordering_download_id_seq'::regclass) NOT NULL,
    section_id integer NOT NULL,
    target_name character varying(255) NOT NULL,
    target_url character varying(255) NOT NULL,
    checksum_name character varying(255),
    checksum_url character varying(255),
    readme_text text,
    display_order integer NOT NULL,
    visible boolean NOT NULL
);


ALTER TABLE espa.ordering_download OWNER TO espa;

--
-- Name: ordering_downloadsection_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_downloadsection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_downloadsection_id_seq OWNER TO espa;

--
-- Name: ordering_downloadsection; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_downloadsection (
    id integer DEFAULT nextval('ordering_downloadsection_id_seq'::regclass) NOT NULL,
    title character varying(255) NOT NULL,
    text text NOT NULL,
    display_order integer NOT NULL,
    visible boolean NOT NULL
);


ALTER TABLE espa.ordering_downloadsection OWNER TO espa;

--
-- Name: ordering_ledapsancillary_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_ledapsancillary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_ledapsancillary_id_seq OWNER TO espa;

--
-- Name: ordering_ledapsancillary; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_ledapsancillary (
    id integer DEFAULT nextval('ordering_ledapsancillary_id_seq'::regclass) NOT NULL,
    "dayAndYear" character varying(7) NOT NULL,
    year integer NOT NULL,
    day integer NOT NULL,
    last_updated timestamp without time zone NOT NULL,
    air text,
    water text,
    pres text,
    ozone text,
    air_filename character varying(1024),
    water_filename character varying(1024),
    pres_filename character varying(1024),
    ozone_filename character varying(1024)
);


ALTER TABLE espa.ordering_ledapsancillary OWNER TO espa;

--
-- Name: ordering_order_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_order_id_seq OWNER TO espa;

--
-- Name: ordering_order; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_order (
    id integer DEFAULT nextval('ordering_order_id_seq'::regclass) NOT NULL,
    orderid character varying(255) NOT NULL,
    email character varying(75) NOT NULL,
    order_date timestamp without time zone NOT NULL,
    completion_date timestamp without time zone,
    status character varying(20) NOT NULL,
    note character varying(2048),
    product_options text NOT NULL,
    order_source character varying(20) NOT NULL,
    ee_order_id character varying(13) NOT NULL,
    user_id integer NOT NULL,
    order_type character varying(50) NOT NULL,
    priority character varying(10) NOT NULL,
    initial_email_sent timestamp without time zone,
    completion_email_sent timestamp without time zone
);


ALTER TABLE espa.ordering_order OWNER TO espa;

--
-- Name: ordering_scene_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_scene_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_scene_id_seq OWNER TO espa;

--
-- Name: ordering_scene; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_scene (
    id integer DEFAULT nextval('ordering_scene_id_seq'::regclass) NOT NULL,
    name character varying(256) NOT NULL,
    note character varying(2048),
    order_id integer NOT NULL,
    product_distro_location character varying(1024) NOT NULL,
    product_dload_url character varying(1024) NOT NULL,
    cksum_distro_location character varying(1024) NOT NULL,
    cksum_download_url character varying(1024) NOT NULL,
    status character varying(30) NOT NULL,
    processing_location character varying(256) NOT NULL,
    completion_date timestamp without time zone,
    log_file_contents text,
    ee_unit_id integer,
    tram_order_id character varying(13),
    sensor_type character varying(50) NOT NULL,
    job_name character varying(255),
    retry_after timestamp without time zone,
    retry_limit integer,
    retry_count integer
);


ALTER TABLE espa.ordering_scene OWNER TO espa;

--
-- Name: ordering_tag_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_tag_id_seq OWNER TO espa;

--
-- Name: ordering_tag; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_tag (
    id integer DEFAULT nextval('ordering_tag_id_seq'::regclass) NOT NULL,
    tag character varying(255) NOT NULL,
    description text,
    last_updated timestamp without time zone
);


ALTER TABLE espa.ordering_tag OWNER TO espa;

--
-- Name: ordering_tramorder_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_tramorder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_tramorder_id_seq OWNER TO espa;

--
-- Name: ordering_tramorder; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_tramorder (
    id integer DEFAULT nextval('ordering_tramorder_id_seq'::regclass) NOT NULL,
    order_id character varying(255) NOT NULL,
    order_date timestamp without time zone
);


ALTER TABLE espa.ordering_tramorder OWNER TO espa;

--
-- Name: ordering_userprofile_id_seq; Type: SEQUENCE; Schema: espa; Owner: espa
--

CREATE SEQUENCE ordering_userprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa.ordering_userprofile_id_seq OWNER TO espa;

--
-- Name: ordering_userprofile; Type: TABLE; Schema: espa; Owner: espa; Tablespace: 
--

CREATE TABLE ordering_userprofile (
    id integer DEFAULT nextval('ordering_userprofile_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    contactid character varying(10) NOT NULL
);


ALTER TABLE espa.ordering_userprofile OWNER TO espa;

--
-- Name: id; Type: DEFAULT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Name: auth_group_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_id_pkey PRIMARY KEY (id);


--
-- Name: auth_group_permissions_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_id_pkey PRIMARY KEY (id);


--
-- Name: auth_message_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_id_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_id_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_id_pkey PRIMARY KEY (id);


--
-- Name: auth_user_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_id_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_id_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_id_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_id_pkey PRIMARY KEY (id);


--
-- Name: django_migrations_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session_session_key_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_session_key_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_configuration_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_configuration
    ADD CONSTRAINT ordering_configuration_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_datapoint_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_datapoint
    ADD CONSTRAINT ordering_datapoint_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_datapoint_tags_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_datapoint_tags
    ADD CONSTRAINT ordering_datapoint_tags_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_datasource_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_datasource
    ADD CONSTRAINT ordering_datasource_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_download_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_download
    ADD CONSTRAINT ordering_download_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_downloadsection_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_downloadsection
    ADD CONSTRAINT ordering_downloadsection_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_ledapsancillary_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_ledapsancillary
    ADD CONSTRAINT ordering_ledapsancillary_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_order_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_order
    ADD CONSTRAINT ordering_order_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_scene_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_scene
    ADD CONSTRAINT ordering_scene_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_tag_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_tag
    ADD CONSTRAINT ordering_tag_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_tramorder_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_tramorder
    ADD CONSTRAINT ordering_tramorder_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_userprofile_id_pkey; Type: CONSTRAINT; Schema: espa; Owner: espa; Tablespace: 
--

ALTER TABLE ONLY ordering_userprofile
    ADD CONSTRAINT ordering_userprofile_id_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX auth_group_name ON auth_group USING btree (name);


--
-- Name: auth_group_permissions_group_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_group_permissions_group_id ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_group_id_permission_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX auth_group_permissions_group_id_permission_id ON auth_group_permissions USING btree (group_id, permission_id);


--
-- Name: auth_group_permissions_permission_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_group_permissions_permission_id ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_message_user_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: auth_permission_content_type_id_codename; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX auth_permission_content_type_id_codename ON auth_permission USING btree (content_type_id, codename);


--
-- Name: auth_user_groups_group_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_user_groups_group_id ON auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_user_groups_user_id ON auth_user_groups USING btree (user_id);


--
-- Name: auth_user_groups_user_id_group_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX auth_user_groups_user_id_group_id ON auth_user_groups USING btree (user_id, group_id);


--
-- Name: auth_user_user_permissions_permission_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_user_user_permissions_permission_id ON auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX auth_user_user_permissions_user_id ON auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_user_permissions_user_id_permission_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX auth_user_user_permissions_user_id_permission_id ON auth_user_user_permissions USING btree (user_id, permission_id);


--
-- Name: auth_user_username; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX auth_user_username ON auth_user USING btree (username);


--
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- Name: django_content_type_app_label_model; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX django_content_type_app_label_model ON django_content_type USING btree (app_label, model);


--
-- Name: django_session_expire_date; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX django_session_expire_date ON django_session USING btree (expire_date);


--
-- Name: ordering_configuration_key; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX ordering_configuration_key ON ordering_configuration USING btree (key);


--
-- Name: ordering_datapoint_tags_datapoint_id_tag_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX ordering_datapoint_tags_datapoint_id_tag_id ON ordering_datapoint_tags USING btree (datapoint_id, tag_id);


--
-- Name: ordering_datapoint_tags_tag_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_datapoint_tags_tag_id ON ordering_datapoint_tags USING btree (tag_id);


--
-- Name: ordering_download_section_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_download_section_id ON ordering_download USING btree (section_id);


--
-- Name: ordering_order_completion_date; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_order_completion_date ON ordering_order USING btree (completion_date);


--
-- Name: ordering_order_email; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_order_email ON ordering_order USING btree (email);


--
-- Name: ordering_order_order_date; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_order_order_date ON ordering_order USING btree (order_date);


--
-- Name: ordering_order_orderid; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX ordering_order_orderid ON ordering_order USING btree (orderid);


--
-- Name: ordering_order_status; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_order_status ON ordering_order USING btree (status);


--
-- Name: ordering_order_user_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_order_user_id ON ordering_order USING btree (user_id);


--
-- Name: ordering_scene_completion_date; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_scene_completion_date ON ordering_scene USING btree (completion_date);


--
-- Name: ordering_scene_name; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_scene_name ON ordering_scene USING btree (name);


--
-- Name: ordering_scene_order_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_scene_order_id ON ordering_scene USING btree (order_id);


--
-- Name: ordering_scene_retry_after; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_scene_retry_after ON ordering_scene USING btree (retry_after);


--
-- Name: ordering_scene_status; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_scene_status ON ordering_scene USING btree (status);


--
-- Name: ordering_scene_tram_order_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE INDEX ordering_scene_tram_order_id ON ordering_scene USING btree (tram_order_id);


--
-- Name: ordering_userprofile_user_id; Type: INDEX; Schema: espa; Owner: espa; Tablespace: 
--

CREATE UNIQUE INDEX ordering_userprofile_user_id ON ordering_userprofile USING btree (user_id);


--
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id);


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id);


--
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: auth_permission_content_type_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id);


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id);


--
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id);


--
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id);


--
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: ordering_order_user_id_fkey; Type: FK CONSTRAINT; Schema: espa; Owner: espa
--

ALTER TABLE ONLY ordering_order
    ADD CONSTRAINT ordering_order_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: espa; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA espa FROM PUBLIC;
REVOKE ALL ON SCHEMA espa FROM postgres;
GRANT ALL ON SCHEMA espa TO postgres;
GRANT ALL ON SCHEMA espa TO espa;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

