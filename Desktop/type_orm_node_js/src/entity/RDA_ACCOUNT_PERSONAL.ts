import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('rda_account_personal') // Replace with your actual table name
export class RdaAccountPersonal {
  @PrimaryGeneratedColumn()
  id!: number;

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaId?: number; // Nullable numeric

  @Column({ type: 'varchar', length: 100, nullable: true })
  title?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  fullName?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  maritalStatus?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  motherMaidenName?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  dob?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  fatherHusbandName?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  mobileNo?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  landlineNo?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  emailAddress?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  idDocumentType?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  idDocumentNumber?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  idIssuanceDate?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  idExpiryDate?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  nationality?: string; // Nullable varchar

  @Column({ type: 'numeric', precision: 3, scale: 0, nullable: true })
  dualNationality?: number; // Nullable numeric

  @Column({ type: 'varchar', length: 100, nullable: true })
  countryOfBirth?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  cityOfBirth?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  countryOfPassport?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  passportNo?: string; // Nullable varchar

  @Column({ type: 'timestamp', nullable: true })
  cd?: Date; // Nullable timestamp

  @Column({ type: 'varchar', length: 100, nullable: true })
  gender?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  dateIssuePassport?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  placeIssuePassport?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  pepStatusSelect?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  pepStatus?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  nextOfKin?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  relationWithKin?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  mobileNoCode?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  landLineCode?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 36, nullable: true })
  createdByUser?: string; // Nullable varchar

  @Column({ type: 'timestamp', nullable: true })
  createdDatetime?: Date; // Nullable timestamp

  @Column({ type: 'varchar', length: 36, nullable: true })
  updatedByUser?: string; // Nullable varchar

  @Column({ type: 'timestamp', nullable: true })
  updatedDatetime?: Date; // Nullable timestamp

  @Column({ type: 'numeric', precision: 3, scale: 0, nullable: true })
  isResidentPakistani?: number; // Nullable numeric

  @Column({ type: 'timestamp', nullable: true })
  ud?: Date; // Nullable timestamp

}
