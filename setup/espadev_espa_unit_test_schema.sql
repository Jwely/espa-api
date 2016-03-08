--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;


SET search_path = espa_unit_test;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.auth_group_id_seq OWNER TO espadev;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE auth_group (
    id integer DEFAULT nextval('auth_group_id_seq'::regclass) NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE espa_unit_test.auth_group OWNER TO espadev;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.auth_group_permissions_id_seq OWNER TO espadev;

--
-- Name: auth_group_permissions; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer DEFAULT nextval('auth_group_permissions_id_seq'::regclass) NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE espa_unit_test.auth_group_permissions OWNER TO espadev;

--
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.auth_message_id_seq OWNER TO espadev;

--
-- Name: auth_message; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE auth_message (
    id integer DEFAULT nextval('auth_message_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE espa_unit_test.auth_message OWNER TO espadev;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.auth_permission_id_seq OWNER TO espadev;

--
-- Name: auth_permission; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer DEFAULT nextval('auth_permission_id_seq'::regclass) NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE espa_unit_test.auth_permission OWNER TO espadev;

--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.auth_user_id_seq OWNER TO espadev;

--
-- Name: auth_user; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
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


ALTER TABLE espa_unit_test.auth_user OWNER TO espadev;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.auth_user_groups_id_seq OWNER TO espadev;

--
-- Name: auth_user_groups; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer DEFAULT nextval('auth_user_groups_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE espa_unit_test.auth_user_groups OWNER TO espadev;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.auth_user_user_permissions_id_seq OWNER TO espadev;

--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE espa_unit_test.auth_user_user_permissions OWNER TO espadev;

--
-- Name: ordering_configuration_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_configuration_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_configuration_id_seq OWNER TO espadev;

--
-- Name: ordering_configuration; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE ordering_configuration (
    id integer DEFAULT nextval('ordering_configuration_id_seq'::regclass) NOT NULL,
    key character varying(255) NOT NULL,
    value character varying(2048) NOT NULL
);


ALTER TABLE espa_unit_test.ordering_configuration OWNER TO espadev;

--
-- Name: ordering_datapoint_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_datapoint_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_datapoint_id_seq OWNER TO espadev;

--
-- Name: ordering_datapoint_tags_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_datapoint_tags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_datapoint_tags_id_seq OWNER TO espadev;

--
-- Name: ordering_download_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_download_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_download_id_seq OWNER TO espadev;

--
-- Name: ordering_downloadsection_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_downloadsection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_downloadsection_id_seq OWNER TO espadev;

--
-- Name: ordering_order_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_order_id_seq OWNER TO espadev;

--
-- Name: ordering_order; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
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


ALTER TABLE espa_unit_test.ordering_order OWNER TO espadev;

--
-- Name: ordering_scene_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_scene_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_scene_id_seq OWNER TO espadev;

--
-- Name: ordering_scene; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
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


ALTER TABLE espa_unit_test.ordering_scene OWNER TO espadev;

--
-- Name: ordering_tag_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_tag_id_seq OWNER TO espadev;

--
-- Name: ordering_userprofile_id_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE ordering_userprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.ordering_userprofile_id_seq OWNER TO espadev;

--
-- Name: ordering_userprofile; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE ordering_userprofile (
    id integer DEFAULT nextval('ordering_userprofile_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    contactid character varying(10) NOT NULL
);


ALTER TABLE espa_unit_test.ordering_userprofile OWNER TO espadev;

--
-- Name: trans_etl_layer_transaction_seq; Type: SEQUENCE; Schema: espa_unit_test; Owner: espadev
--

CREATE SEQUENCE trans_etl_layer_transaction_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE espa_unit_test.trans_etl_layer_transaction_seq OWNER TO espadev;

--
-- Name: trans_etl_layer; Type: TABLE; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE TABLE trans_etl_layer (
    transaction integer DEFAULT nextval('trans_etl_layer_transaction_seq'::regclass) NOT NULL,
    table_name character varying(50) NOT NULL,
    table_id integer NOT NULL,
    trigger_date timestamp without time zone NOT NULL,
    trigger_read boolean DEFAULT false,
    read_date timestamp without time zone,
    trigger_count integer DEFAULT 0
);


ALTER TABLE espa_unit_test.trans_etl_layer OWNER TO espadev;

--
-- Name: auth_group_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_id_pkey PRIMARY KEY (id);


--
-- Name: auth_group_permissions_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_id_pkey PRIMARY KEY (id);


--
-- Name: auth_message_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_id_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_id_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_id_pkey PRIMARY KEY (id);


--
-- Name: auth_user_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_id_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_configuration_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY ordering_configuration
    ADD CONSTRAINT ordering_configuration_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_order_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY ordering_order
    ADD CONSTRAINT ordering_order_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_scene_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY ordering_scene
    ADD CONSTRAINT ordering_scene_id_pkey PRIMARY KEY (id);


--
-- Name: ordering_userprofile_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY ordering_userprofile
    ADD CONSTRAINT ordering_userprofile_id_pkey PRIMARY KEY (id);


--
-- Name: trans_etl_layer_table_name_table_id_pkey; Type: CONSTRAINT; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

ALTER TABLE ONLY trans_etl_layer
    ADD CONSTRAINT trans_etl_layer_table_name_table_id_pkey PRIMARY KEY (table_name, table_id);


--
-- Name: auth_group_name; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX auth_group_name ON auth_group USING btree (name);


--
-- Name: auth_group_permissions_group_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_group_permissions_group_id ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_group_id_permission_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX auth_group_permissions_group_id_permission_id ON auth_group_permissions USING btree (group_id, permission_id);


--
-- Name: auth_group_permissions_permission_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_group_permissions_permission_id ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_message_user_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: auth_permission_content_type_id_codename; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX auth_permission_content_type_id_codename ON auth_permission USING btree (content_type_id, codename);


--
-- Name: auth_user_groups_group_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_user_groups_group_id ON auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_user_groups_user_id ON auth_user_groups USING btree (user_id);


--
-- Name: auth_user_groups_user_id_group_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX auth_user_groups_user_id_group_id ON auth_user_groups USING btree (user_id, group_id);


--
-- Name: auth_user_user_permissions_permission_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_user_user_permissions_permission_id ON auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX auth_user_user_permissions_user_id ON auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_user_permissions_user_id_permission_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX auth_user_user_permissions_user_id_permission_id ON auth_user_user_permissions USING btree (user_id, permission_id);


--
-- Name: auth_user_username; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX auth_user_username ON auth_user USING btree (username);


--
-- Name: ordering_configuration_key; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX ordering_configuration_key ON ordering_configuration USING btree (key);


--
-- Name: ordering_order_completion_date; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_completion_date ON ordering_order USING btree (completion_date);


--
-- Name: ordering_order_completion_email_sent; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_completion_email_sent ON ordering_order USING btree (completion_email_sent);


--
-- Name: ordering_order_email; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_email ON ordering_order USING btree (email);


--
-- Name: ordering_order_initial_email_sent; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_initial_email_sent ON ordering_order USING btree (initial_email_sent);


--
-- Name: ordering_order_order_date; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_order_date ON ordering_order USING btree (order_date);


--
-- Name: ordering_order_order_type; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_order_type ON ordering_order USING btree (order_type);


--
-- Name: ordering_order_orderid; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX ordering_order_orderid ON ordering_order USING btree (orderid);


--
-- Name: ordering_order_priority; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_priority ON ordering_order USING btree (priority);


--
-- Name: ordering_order_status; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_status ON ordering_order USING btree (status);


--
-- Name: ordering_order_user_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_order_user_id ON ordering_order USING btree (user_id);


--
-- Name: ordering_scene_completion_date; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_scene_completion_date ON ordering_scene USING btree (completion_date);


--
-- Name: ordering_scene_name; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_scene_name ON ordering_scene USING btree (name);


--
-- Name: ordering_scene_order_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_scene_order_id ON ordering_scene USING btree (order_id);


--
-- Name: ordering_scene_retry_after; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_scene_retry_after ON ordering_scene USING btree (retry_after);


--
-- Name: ordering_scene_sensor_type; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_scene_sensor_type ON ordering_scene USING btree (sensor_type);


--
-- Name: ordering_scene_status; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX ordering_scene_status ON ordering_scene USING btree (status);


--
-- Name: ordering_userprofile_user_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE UNIQUE INDEX ordering_userprofile_user_id ON ordering_userprofile USING btree (user_id);


--
-- Name: trans_etl_layer_table_id; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX trans_etl_layer_table_id ON trans_etl_layer USING btree (table_id);


--
-- Name: trans_etl_layer_transaction; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX trans_etl_layer_transaction ON trans_etl_layer USING btree (transaction);


--
-- Name: trans_etl_layer_trigger_count; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX trans_etl_layer_trigger_count ON trans_etl_layer USING btree (trigger_count);


--
-- Name: trans_etl_layer_trigger_date; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX trans_etl_layer_trigger_date ON trans_etl_layer USING btree (trigger_date);


--
-- Name: trans_etl_layer_trigger_date_trigger_read; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX trans_etl_layer_trigger_date_trigger_read ON trans_etl_layer USING btree (trigger_date, trigger_read);


--
-- Name: trans_etl_layer_trigger_read; Type: INDEX; Schema: espa_unit_test; Owner: espadev; Tablespace: 
--

CREATE INDEX trans_etl_layer_trigger_read ON trans_etl_layer USING btree (trigger_read);


--
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id);


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id);


--
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id);


--
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id);


--
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id);


--
-- Name: ordering_order_user_id_4c883492162df004_fk_auth_user_id; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY ordering_order
    ADD CONSTRAINT ordering_order_user_id_4c883492162df004_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ordering_scene_order_id_fkey; Type: FK CONSTRAINT; Schema: espa_unit_test; Owner: espadev
--

ALTER TABLE ONLY ordering_scene
    ADD CONSTRAINT ordering_scene_order_id_fkey FOREIGN KEY (order_id) REFERENCES ordering_order(id);


--
-- Name: espa_unit_test; Type: ACL; Schema: -; Owner: postgres
--


