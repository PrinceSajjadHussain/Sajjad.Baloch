import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('rda_account_kyc') // Replace with your actual table name
export class RdaAccountKyc {

  @PrimaryGeneratedColumn()
  id!: number; // Primary key, auto-generated

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaStatus?: number; // Nullable numeric

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaId?: number; // Nullable numeric

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  roleType?: number; // Nullable numeric

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  userId?: number; // Nullable numeric

  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' }) // Default to current timestamp
  timeIn!: Date; // Non-nullable timestamp

}
