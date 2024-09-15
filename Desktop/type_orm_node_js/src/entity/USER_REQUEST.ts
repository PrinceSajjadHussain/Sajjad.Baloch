import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';
import { IsOptional, IsString, IsNumber, IsDate, Length, IsIn, IsEmail } from 'class-validator';

@Entity({ name: 'USER_REQUEST' })
export class USER_REQUEST {
  @PrimaryGeneratedColumn()
  ID: string = "";

  @Column({ name: 'CREATED_BY_USER', nullable: true, default: null, type: 'varchar2', length: 255 })
  @IsOptional()
  @IsString()
  @Length(0, 255)
  CREATED_BY_USER: string = '';

  @Column({ name: 'CREATED_DATETIME', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  CREATED_DATETIME: Date = new Date();

  @Column({ name: 'UPDATED_BY_USER', nullable: true, default: null, type: 'varchar2', length: 255 })
  @IsOptional()
  @IsString()
  @Length(0, 255)
  UPDATED_BY_USER: string = '';

  @Column({ name: 'UPDATED_DATETIME', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  UPDATED_DATETIME: Date = new Date();

  @Column({ name: 'BOOL_SPARE1VAL', type: 'number', nullable: true, default: 0 })
  @IsOptional()
  @IsIn([0, 1])
  BOOL_SPARE1VAL: 1 | 0 | null = 0;

  @Column({ name: 'BOOL_SPARE2VAL', type: 'number', nullable: true, default: 0 })
  @IsOptional()
  @IsIn([0, 1])
  BOOL_SPARE2VAL: 1 | 0 | null = 0;

  @Column({ name: 'BOOL_SPARE3VAL', type: 'number', nullable: true, default: 0 })
  @IsOptional()
  @IsIn([0, 1])
  BOOL_SPARE3VAL: 1 | 0 | null = 0;

  @Column({ name: 'BOOL_SPARE4VAL', type: 'number', nullable: true, default: 0 })
  @IsOptional()
  @IsIn([0, 1])
  BOOL_SPARE4VAL: 1 | 0 | null = 0;

  @Column({ name: 'BOOL_SPARE5VAL', type: 'number', nullable: true, default: 0 })
  @IsOptional()
  @IsIn([0, 1])
  BOOL_SPARE5VAL: 1 | 0 | null = 0;

  @Column({ name: 'CREATED_BY', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  CREATED_BY: number = 0;

  @Column({ name: 'DATE_CREATED', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  DATE_CREATED: Date = new Date();

  @Column({ name: 'INT_SPARE1VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE1VAL: number = 0;

  @Column({ name: 'INT_SPARE2VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE2VAL: number = 0;

  @Column({ name: 'INT_SPARE3VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE3VAL: number = 0;

  @Column({ name: 'INT_SPARE4VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE4VAL: number = 0;

  @Column({ name: 'INT_SPARE5VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE5VAL: number = 0;

  @Column({ name: 'IS_ENABLED', type: 'number', nullable: true, default: 0 })
  @IsOptional()
  @IsIn([0, 1])
  IS_ENABLED: 1 | 0 | null = 1;

  @Column({ name: 'LAST_UPDATED', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  LAST_UPDATED: Date = new Date();

  @Column({ name: 'MODIFIED_BY', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  MODIFIED_BY: number = 0;

  @Column({ name: 'STR_SPARE1VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE1VAL: string = '';

  @Column({ name: 'STR_SPARE2VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE2VAL: string = '';

  @Column({ name: 'STR_SPARE3VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE3VAL: string = '';

  @Column({ name: 'STR_SPARE4VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE4VAL: string = '';

  @Column({ name: 'STR_SPARE5VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE5VAL: string = '';

  @Column({ name: 'USER_REQUEST', type: 'clob', nullable: true, default: '' })
  @IsOptional()
  @IsString()
  USER_REQUEST: string = '';

  @Column({ name: 'BACK_END_MODULE', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  BACK_END_MODULE: number = 0;

  @Column({ name: 'MODULE_STATUS', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  MODULE_STATUS: number = 0;

  @Column({ name: 'STR_SPARE6VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE6VAL: string = '';

  @Column({ name: 'STR_SPARE7VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE7VAL: string = '';

  @Column({ name: 'DATE_SPARE1VAL', type: 'timestamp', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE1VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE2VAL', type: 'timestamp', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE2VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE3VAL', type: 'timestamp', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE3VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE4VAL', type: 'timestamp', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE4VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE5VAL', type: 'timestamp', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE5VAL: Date = new Date();

  @Column({ name: 'STR_SPARE8VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE8VAL: string = '';

  @Column({ name: 'STR_SPARE9VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE9VAL: string = '';

  @Column({ name: 'STR_SPARE10VAL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  STR_SPARE10VAL: string = '';

  @Column({ name: 'ROOM_ID', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  ROOM_ID: string = '';

  @Column({ name: 'VIDEO_KYC_USER_ID', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  VIDEO_KYC_USER_ID: string = '';

  @Column({ name: 'VIDEO_KYC_USER_NAME', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  VIDEO_KYC_USER_NAME: string = '';

  @Column({ name: 'OCR_COMPARISION', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 256)
  OCR_COMPARISION: string = '';

  @Column({ name: 'ACCOUNT_OPENING_DATE', type: 'timestamp', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  ACCOUNT_OPENING_DATE: Date = new Date();

  @Column({ name: 'PBC_EMAIL', length: 256, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsEmail()
  PBC_EMAIL: string = '';

  constructor() {}
}
