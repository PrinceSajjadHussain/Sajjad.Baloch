import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('rda_account_log') // Replace 'your_table_name' with the actual name of your database table
export class RdaAccountLog {

  @PrimaryGeneratedColumn()
  id: number = 0; // Primary key with auto-increment

  @Column({ type: 'int', nullable: true, default: null })
  rdaStatus: number | null = null;

  @Column({ type: 'int', nullable: true, default: null })
  rdaId: number | null = null;

  @Column({ type: 'int', nullable: true, default: null })
  roleType: number | null = null;

  @Column({ type: 'int', nullable: true, default: null })
  userId: number | null = null;

  @Column({ type: 'timestamp', nullable: false, default: () => 'CURRENT_TIMESTAMP' })
  timeIn: Date = new Date(); // Timestamp with default value of current timestamp
}
