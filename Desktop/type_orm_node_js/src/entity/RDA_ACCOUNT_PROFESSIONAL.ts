import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  Timestamp
} from 'typeorm';

@Entity('rda_account_personal') // Replace with your actual table name
export class RdaAccountPersonal {
  @PrimaryGeneratedColumn()
  id!: number; // Non-nullable numeric primary key

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaId?: number; // Nullable numeric

  @Column({ type: 'varchar', length: 100, nullable: true })
  professionType?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  natureOfBusiness?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  businessLocation?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  businessLocationPlace?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  sourceOfFunds?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  averageMonthlySalary?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  expectedMonthlyTurnover?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  nomineeCounterParty?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  nameEmployer?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  titlePosition?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  otherProfessionType?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  otherDependentOn?: string; // Nullable varchar

  @CreateDateColumn({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  cd!: Timestamp; // Creation timestamp (non-nullable)

  @Column({ type: 'varchar', length: 100, nullable: true })
  occupation?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  province?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 200, nullable: true })
  employerAddress?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  employerBusiness?: string; // Nullable varchar

  @UpdateDateColumn({ type: 'timestamp', nullable: true })
  ud?: Timestamp; // Update timestamp (nullable)
}
