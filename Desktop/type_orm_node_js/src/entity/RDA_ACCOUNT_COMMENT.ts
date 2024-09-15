import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('rda_account_comment') // Replace 'your_table_name' with the actual name of your database table
export class RdaAccountComment {

  @PrimaryGeneratedColumn('increment') // Use 'increment' for auto-incremented number
  id: number = 0; // Use 'number' type for primary key

  @Column({ type: 'numeric', precision: 38, scale: 0, nullable: true, default: null })
  rdaId: number | null = null;

  @Column({ type: 'varchar', length: 200, nullable: true, default: '' })
  dept: string = '';

  @Column({ type: 'varchar', length: 3000, nullable: true, default: '' })
  deptComment: string = '';

  @Column({ type: 'varchar', length: 200, nullable: true, default: '' })
  commentBy: string = '';

  @Column({ type: 'timestamp', precision: 6, nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  createdOn: Date | null = null;
}
