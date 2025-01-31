CREATE DATABASE IF NOT EXISTS `temperaturas`;
USE `temperaturas`;
DROP TABLE IF EXISTS `temperaturas`;
DROP TABLE IF EXISTS `fronteras`;
DROP TABLE IF EXISTS `paises`;

CREATE TABLE `paises` (
  `idpais` int NOT NULL AUTO_INCREMENT,
  `cca2` varchar(2) NOT NULL,
  `cca3` varchar(3) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `capital` varchar(255) NOT NULL,
  `region` varchar(255) NOT NULL,
  `subregion` varchar(255) NOT NULL,
  `miembroNU` bit(1) NOT NULL,
  `latitud` float DEFAULT NULL,
  `longitud` float DEFAULT NULL,
  PRIMARY KEY (`idpais`)
) ENGINE=InnoDB AUTO_INCREMENT=107;


CREATE TABLE `fronteras` (
  `idfronteras` int NOT NULL AUTO_INCREMENT,
  `idpais` int NOT NULL,
  `cca3_frontera` varchar(3) NOT NULL,
  PRIMARY KEY (`idfronteras`),
  KEY `fk_frontera_pais_idx` (`idpais`),
  CONSTRAINT `fk_frontera_pais` FOREIGN KEY (`idpais`) REFERENCES `paises` (`idpais`)
) ENGINE=InnoDB AUTO_INCREMENT=367;


CREATE TABLE `temperaturas` (
  `idtemperaturas` int NOT NULL AUTO_INCREMENT,
  `idpais` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `temperatura` float NOT NULL,
  `sensacion` float NOT NULL,
  `minima` float NOT NULL,
  `maxima` float NOT NULL,
  `humedad` float NOT NULL,
  `amanecer` time NOT NULL,
  `atardecer` time NOT NULL,
  PRIMARY KEY (`idtemperaturas`),
  KEY `fk_pais_temperatura_idx` (`idpais`),
  CONSTRAINT `fk_pais_temperatura` FOREIGN KEY (`idpais`) REFERENCES `paises` (`idpais`)
) ENGINE=InnoDB AUTO_INCREMENT=121;
