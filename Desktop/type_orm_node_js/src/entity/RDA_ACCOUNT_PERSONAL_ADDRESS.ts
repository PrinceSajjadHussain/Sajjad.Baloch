import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity('rda_account_personal_address') // Replace 'address_table' with the actual name of your database table
export class RdaAccountPersonalAddress {
  
  @PrimaryGeneratedColumn()
  id: number = 0;

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  rdaId: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  countryOfResidence: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  city: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  states: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  street: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  mailAddress: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  zipPostalPoBox: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  cd: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  townArea: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  flateAreaBuilding: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  province: string = '';

  @Column({ type: 'varchar', length: 255, nullable: true, default: '' })
  ud: string = '';
}
