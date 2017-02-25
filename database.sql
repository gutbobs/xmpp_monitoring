-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost:3306
-- Generation Time: Feb 25, 2017 at 02:54 PM
-- Server version: 5.7.17-0ubuntu0.16.04.1
-- PHP Version: 7.0.15-0ubuntu0.16.04.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Monitoring`
--

-- --------------------------------------------------------

--
-- Table structure for table `Hosts`
--

CREATE TABLE `Hosts` (
  `ID` int(11) NOT NULL,
  `HOSTNAME` varchar(30) NOT NULL,
  `FIRSTSEEN` datetime DEFAULT CURRENT_TIMESTAMP,
  `LASTSEEN` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Host_State`
--

CREATE TABLE `Host_State` (
  `ID` int(11) NOT NULL,
  `HOSTID` int(11) NOT NULL,
  `CURRENTSTATE` int(11) NOT NULL,
  `LASTSTATE` int(11) NOT NULL,
  `LASTSTATECHANGE` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Processes`
--

CREATE TABLE `Processes` (
  `ID` int(11) NOT NULL,
  `PROCESSNAME` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Process_State`
--

CREATE TABLE `Process_State` (
  `ID` int(11) NOT NULL,
  `PROCESSID` int(11) NOT NULL,
  `CURRENTSTATE` int(11) NOT NULL,
  `LASTSTATE` int(11) NOT NULL,
  `LASTSTATECHANGE` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Process_tmp`
--

CREATE TABLE `Process_tmp` (
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
  ADD UNIQUE KEY `HOSTNAME` (`HOSTNAME`),
  ADD KEY `ID` (`ID`);

--
-- Indexes for table `Host_State`
--
ALTER TABLE `Host_State`
  ADD UNIQUE KEY `HOSTID` (`HOSTID`),
  ADD KEY `ID` (`ID`);

--
-- Indexes for table `Processes`
--
ALTER TABLE `Processes`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `PROCESSNAME` (`PROCESSNAME`),
  ADD KEY `ID` (`ID`);

--
-- Indexes for table `Process_State`
--
ALTER TABLE `Process_State`
  ADD KEY `ID` (`ID`);

--
-- Indexes for table `Process_tmp`
--
ALTER TABLE `Process_tmp`
  ADD UNIQUE KEY `ID` (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Hosts`
--
ALTER TABLE `Hosts`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;
--
-- AUTO_INCREMENT for table `Host_State`
--
ALTER TABLE `Host_State`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `Processes`
--
ALTER TABLE `Processes`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;
--
-- AUTO_INCREMENT for table `Process_State`
--
ALTER TABLE `Process_State`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;
--
-- AUTO_INCREMENT for table `Process_tmp`
--
ALTER TABLE `Process_tmp`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=407;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
