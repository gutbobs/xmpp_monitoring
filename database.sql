-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 21, 2016 at 06:45 PM
-- Server version: 5.5.52-0+deb8u1
-- PHP Version: 5.6.27-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `Monitoring`
--

-- --------------------------------------------------------

--
-- Table structure for table `Hosts`
--

CREATE TABLE IF NOT EXISTS `Hosts` (
`ID` int(11) NOT NULL,
  `HOSTNAME` varchar(30) NOT NULL,
  `FIRSTSEEN` datetime NOT NULL,
  `LASTSEEN` datetime NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Host_State`
--

CREATE TABLE IF NOT EXISTS `Host_State` (
`ID` int(11) NOT NULL,
  `HOSTID` int(11) NOT NULL,
  `CURRENTSTATE` int(11) NOT NULL,
  `LASTSTATE` int(11) NOT NULL,
  `LASTSTATECHANGE` datetime NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Processes`
--

CREATE TABLE IF NOT EXISTS `Processes` (
`ID` int(11) NOT NULL,
  `PROCESSNAME` varchar(30) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Process_State`
--

CREATE TABLE IF NOT EXISTS `Process_State` (
`ID` int(11) NOT NULL,
  `PROCESSID` int(11) NOT NULL,
  `CURRENTSTATE` int(11) NOT NULL,
  `LASTSTATE` int(11) NOT NULL,
  `LASTSTATECHANGE` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Process_tmp`
--

CREATE TABLE IF NOT EXISTS `Process_tmp` (
  `ID` int(11) NOT NULL,
  `UID` varchar(36) NOT NULL,
  `REQUESTTIME` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `PROCESSID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Hosts`
--
ALTER TABLE `Hosts`
 ADD UNIQUE KEY `HOSTNAME` (`HOSTNAME`), ADD KEY `ID` (`ID`);

--
-- Indexes for table `Host_State`
--
ALTER TABLE `Host_State`
 ADD UNIQUE KEY `HOSTID` (`HOSTID`), ADD KEY `ID` (`ID`);

--
-- Indexes for table `Processes`
--
ALTER TABLE `Processes`
 ADD PRIMARY KEY (`ID`), ADD UNIQUE KEY `PROCESSNAME` (`PROCESSNAME`), ADD KEY `ID` (`ID`);

--
-- Indexes for table `Process_State`
--
ALTER TABLE `Process_State`
 ADD KEY `ID` (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Hosts`
--
ALTER TABLE `Hosts`
MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `Host_State`
--
ALTER TABLE `Host_State`
MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `Processes`
--
ALTER TABLE `Processes`
MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=9;
--
-- AUTO_INCREMENT for table `Process_State`
--
ALTER TABLE `Process_State`
MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=7;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

