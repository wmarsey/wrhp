--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: wikicontent; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE wikicontent (
    revid integer NOT NULL,
    pageid integer,
    content text,
    domain character varying(255)
);


--
-- Name: wikifetched; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE wikifetched (
    pageid integer NOT NULL,
    title character varying(255),
    language character varying(255) NOT NULL
);


--
-- Name: wikirevisions; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE wikirevisions (
    revid integer NOT NULL,
    parentid integer NOT NULL,
    pageid integer NOT NULL,
    username character varying(255),
    userid integer,
    "time" timestamp without time zone,
    size integer,
    comment character varying(2048),
    domain character varying(255) NOT NULL
);


--
-- Name: wikitrajectory; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE wikitrajectory (
    revid1 integer NOT NULL,
    revid2 integer NOT NULL,
    distance integer,
    domain character varying NOT NULL
);


--
-- Name: wikiweights; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE wikiweights (
    revid integer NOT NULL,
    domain character(255) NOT NULL,
    maths integer,
    citations integer,
    filesimages integer,
    links integer,
    structure integer,
    normal integer,
    gradient real,
    complete boolean
);


--
-- Name: wikifetched_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY wikifetched
    ADD CONSTRAINT wikifetched_pkey PRIMARY KEY (pageid, language);


--
-- Name: wikirevisions_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY wikirevisions
    ADD CONSTRAINT wikirevisions_pkey PRIMARY KEY (revid, domain);


--
-- Name: wikitrajectory_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY wikitrajectory
    ADD CONSTRAINT wikitrajectory_pkey PRIMARY KEY (revid1, revid2, domain);


--
-- Name: wikiweights_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY wikiweights
    ADD CONSTRAINT wikiweights_pkey PRIMARY KEY (revid, domain);


--
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM wm613;
SET SESSION AUTHORIZATION postgres;
GRANT ALL ON SCHEMA public TO tora;
RESET SESSION AUTHORIZATION;
SET SESSION AUTHORIZATION postgres;
GRANT ALL ON SCHEMA public TO pjm;
RESET SESSION AUTHORIZATION;
SET SESSION AUTHORIZATION postgres;
GRANT ALL ON SCHEMA public TO postgres;
RESET SESSION AUTHORIZATION;
SET SESSION AUTHORIZATION postgres;
GRANT ALL ON SCHEMA public TO wm613;
RESET SESSION AUTHORIZATION;


--
-- PostgreSQL database dump complete
--

