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

DROP TABLE wikicontent;

--
-- Name: wikifetched; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

DROP TABLE wikifetched;

--
-- Name: wikirevisions; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

DROP TABLE wikirevisions;


--
-- Name: wikitrajectory; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

DROP TABLE wikitrajectory;

--
-- Name: wikiweights; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

DROP TABLE wikiweights;

--
-- PostgreSQL database dump complete
--

