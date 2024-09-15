import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('rda_account_extra') // Replace 'your_table_name' with the actual name of your database table
export class RdaAccountExtra {

  @PrimaryGeneratedColumn()
  id: number = 0; // Primary key with auto-increment

  @Column({ type: 'int', nullable: true, default: null })
  rdaId: number | null = null;

  @Column({ type: 'varchar', length: 200, nullable: true, default: '' })
  strOne: string = '';

  @Column({ type: 'varchar', length: 200, nullable: true, default: '' })
  strTwo: string = '';

  @Column({ type: 'varchar', length: 200, nullable: true, default: '' })
  strThree: string = '';

  @Column({ type: 'varchar', length: 200, nullable: true, default: '' })
  strFour: string = '';

  @Column({ type: 'varchar', length: 200, nullable: true, default: '' })
  strFive: string = '';

  @Column({ type: 'int', nullable: true, default: null })
  intOne: number | null = null;

  @Column({ type: 'int', nullable: true, default: null })
  intTwo: number | null = null;

  @Column({ type: 'int', nullable: true, default: null })
  intThree: number | null = null;

  @Column({ type: 'int', nullable: true, default: null })
  intFour: number | null = null;

  @Column({ type: 'int', nullable: true, default: null })
  intFive: number | null = null;

  @Column({ type: 'timestamp', nullable: true, default: null })
  cd: Date | null = null;

  @Column({ type: 'timestamp', precision: 6, nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  ud: Date | null = null;
}
