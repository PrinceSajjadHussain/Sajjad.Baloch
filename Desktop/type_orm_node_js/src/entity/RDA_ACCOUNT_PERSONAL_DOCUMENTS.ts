import {
  Column,
  CreateDateColumn,
  Entity,
  PrimaryGeneratedColumn,
  Timestamp
} from 'typeorm';

@Entity('rda_account_personal_documents') // Replace with your actual table name
export class RdaAccountPersonalDocuments {
  @PrimaryGeneratedColumn()
  id!: number; // Non-nullable numeric primary key

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaId?: number; // Nullable numeric

  @Column({ type: 'varchar', length: 400, nullable: true })
  fatcaFormUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  crsForm?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  ssCard?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  cnicFrontUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  cnicBackUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  passportUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  nrpStatusUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  incomeUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  photoUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  professionProofUrl?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 400, nullable: true })
  signUrl?: string; // Nullable varchar

  @CreateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  cd!: Timestamp; // Creation timestamp (non-nullable)
}
