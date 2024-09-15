import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('rda_account_personal_banks') // Replace with your actual table name
export class RdaAccountPersonalBanks {

  @PrimaryGeneratedColumn()
  id!: number; // Primary key, auto-generated

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  rdaId?: number; // Nullable numeric

  @Column({ type: 'varchar', length: 100, nullable: true })
  bankName?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  remittingAccountNumber?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  bankCountry?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  bankCity?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  bankAccountTitle?: string; // Nullable varchar

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  chequeBook?: number; // Nullable numeric

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  debitCard?: number; // Nullable numeric

  @Column({ type: 'varchar', length: 100, nullable: true })
  debitCardType?: string; // Nullable varchar

  @Column({ type: 'varchar', length: 100, nullable: true })
  nameOnCard?: string; // Nullable varchar

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  supplementaryCard?: number; // Nullable numeric

  @Column({ type: 'varchar', length: 100, nullable: true })
  nameOnSupplementaryCard?: string; // Nullable varchar

  @Column({ type: 'timestamp', nullable: true })
  cd?: Date; // Nullable timestamp

  @Column({ type: 'varchar', length: 100, nullable: true })
  estatement?: string; // Nullable varchar

  @Column({ type: 'numeric', precision: 10, scale: 0, nullable: true })
  chequeBookFcy?: number; // Nullable numeric

  @Column({ type: 'timestamp', nullable: true })
  ud?: Date; // Nullable timestamp

}
