export interface ResumeData {
  name: Name;
  aboutMe: AboutMe;
  education: Education[];
  experience: Experience[];
  contact: Contact[];
  skills: Skill[];
  customSections: CustomSection[];
}

export interface Name {
  firstName: string;
  lastName: string;
}

export interface AboutMe {
  description: string;
  polishedDescription?: string; // AI-improved version
}

export interface Education {
  id: string;
  degree: string;
  institution: string;
  startDate: string;
  endDate: string;
  description: string;
  polishedDescription?: string; // AI-improved version
}

export interface Experience {
  id: string;
  title: string;
  company: string;
  startDate: string;
  endDate: string;
  description: string;
  keywords: string[];
  polishedDescription?: string; // AI-improved version
}

export interface Contact {
  id: string;
  type: string;
  value: string;
}

export interface Skill {
  id: string;
  skill: string;
}

export interface CustomSection {
  id: string;
  title: string;
  content: string;
}

export interface UpdateMessage {
  section: string;
  entryId: string;
  changeType: 'add' | 'update' | 'delete';
  content: any;
}

export interface PolishRequest {
  section: string;
  entryId: string;
  content: any;
}