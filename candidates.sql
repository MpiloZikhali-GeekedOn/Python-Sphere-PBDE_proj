BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS candidates (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	votes INTEGER, 
	department VARCHAR(100) NOT NULL, 
	contribution VARCHAR(100) NOT NULL, 
	position VARCHAR(9) NOT NULL, 
	political_party VARCHAR(100) NOT NULL, 
	date_created DATETIME, 
	profile_picture VARCHAR(255), 
	proof_document VARCHAR(255), 
	PRIMARY KEY (id)
);
INSERT INTO "candidates" VALUES (1,'Lina',0,'Information Technology','Built a bridge','President','Economic Freedom Fighters','2025-03-12 22:01:48.495665','uploads/447864426_991753815812848_9187034707201724299_n.jpg','uploads/download.pdf'),
 (2,'Siya',0,'Information Systems','leader of living vallue framework','President','SASCO','2025-03-12 23:15:50.277186','uploads/447864426_991753815812848_9187034707201724299_n.jpg','uploads/Order_-_0K8TN.pdf'),
 (3,'Sipho',0,'Applied Sciences','Community Building','Treasurer','SASCO','2025-03-12 23:18:38.495348','uploads/447864426_991753815812848_9187034707201724299_n.jpg','uploads/download_1.pdf'),
 (4,'Hailey',0,'Communications','Tech & Communication','President','Economic Freedom Fighters','2025-03-12 23:19:23.889467','uploads/447864426_991753815812848_9187034707201724299_n.jpg','uploads/download_1.pdf');
COMMIT;
