import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('RDA_ACCOUNT') // Replace 'your_table_name' with the actual name of your database table
export class YourEntityName {

  @PrimaryGeneratedColumn()
  id!: number;  // Use definite assignment assertion

  @Column({ type: 'varchar', length: 100, nullable: true })
  rdaCurrencyType: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  rdaAccountNature: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  rdaAccountType: string | null = null;

  @Column({ type: 'varchar', length: 400, nullable: true })
  rdaAccountNo: string | null = null;

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  accountHolder: number | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  cif: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  accountNo: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  documentsVerified: string | null = null;

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  verisysUploadStatus: number | null = null;

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaStatus: number | null = null;

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaComplianceStatus: number | null = null;

  @Column({ type: 'varchar', length: 400, nullable: true })
  rdaComplianceComments: string | null = null;

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaAsuStatus: number | null = null;

  @Column({ type: 'varchar', length: 400, nullable: true })
  rdaAsuComments: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  asuVerifiedQOne: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  asuVerifiedQTwo: string | null = null;

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaCcuStatus: number | null = null;

  @Column({ type: 'varchar', length: 400, nullable: true })
  rdaCcuComments: string | null = null;

  @Column({ type: 'timestamp', nullable: true })
  ud: Date | null = null;

  @Column({ type: 'timestamp', nullable: true })
  cd: Date | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  lcyAccountNo: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  iban: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  shadowIban: string | null = null;

  @Column({ type: 'varchar', length: 20, nullable: true })
  rmId: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  asuVerifiedQThree: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  asuVerifiedQFour: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  rmRegion: string | null = null;

  @Column({ type: 'numeric', precision: 3, scale: 0, nullable: true })
  rdaFormStatus: number | null = null;

  @Column({ type: 'numeric', precision: 2, scale: 0, nullable: true })
  videoKyc: number | null = null;

  @Column({ type: 'varchar', length: 300, nullable: true })
  videoKycUrl: string | null = null;

  @Column({ type: 'varchar', length: 50, nullable: true })
  videoKycRoomId: string | null = null;

  @Column({ type: 'varchar', length: 200, nullable: true })
  videoKycComment: string | null = null;

  @Column({ type: 'varchar', length: 50, nullable: true })
  videoKycUserId: string | null = null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  videoKycUserName: string | null = null;
}
